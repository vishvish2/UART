import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge


@cocotb.test()
async def uart_tx_tb(dut):

    # 100MHz clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Data width, number of bits in the data being transmitted
    data_width = int(dut.DATA_WIDTH.value)

    # Baud count max value to keep track of baud ticks
    baud_max_count = int(dut.BAUD_MAX_COUNT.value)

    # Assert reset for few clock cycles
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    # UART state should be IDLE and assert READY in AXI interface
    # In IDLE, TX line should be held high
    for _ in range((data_width * baud_max_count)):  # number of clock cycles equal to data width
        await RisingEdge(dut.clk)
        assert dut.TX.value == 1, (
            f"expected TX = 1, got TX = {dut.TX.value}"
        )
        assert dut.tx_ready.value == 1, (
            f"expected tx_ready = 1, got tx_ready = {dut.tx_ready.value}"
        )

    # Test byte
    test_bitstream = 0b10010101
    dut.data.value = test_bitstream

    # VALID not asserted, TX line should still be held high
    for _ in range((data_width * baud_max_count)):
        await RisingEdge(dut.clk)
        assert dut.TX.value == 1, (
            f"expected TX = 1, got TX = {dut.TX.value}"
        )

    # Assert AXI VALID signal for one clock cycle
    dut.tx_valid.value = 1
    await RisingEdge(dut.clk)                           # Wait for VALID to get recognised
    assert dut.tx_ready.value == 1, (
            f"expected tx_ready = 1, got tx_ready = {dut.tx_ready.value}"   # VALID and READY are 1 simultaneously
        )
    await RisingEdge(dut.clk)                           # Hold VALID high for one clock cycle
    assert dut.tx_ready.value == 0, (
            f"expected tx_ready = 0, got tx_ready = {dut.tx_ready.value}"   # READY is deasserted, handshake successful
        )
    dut.tx_valid.value = 0                              # Only now deassert VALID (AXI handshake rules)

    # UART state should be START, transitions to 0 for one bit period (period between each baud tick)
    for _ in range(baud_max_count - 1):                 # -1 because one clock cycle used for testing handshake
        await RisingEdge(dut.clk)
        assert dut.TX.value == 0, (
            f"expected TX = 0, got TX = {dut.TX.value}"
        )
        assert dut.tx_ready.value == 0, (
            f"expected tx_ready = 0, got tx_ready = {dut.tx_ready.value}"  # READY should remain deasserted
        )

    # This should be ignored until after IDLE state is reached again
    test_bitstream_2 = 0b01001110
    dut.data.value = test_bitstream_2
    dut.tx_valid.value = 1

    # UART state should be DATA, compare TX against data, LSB transmits first
    for n in range(data_width):
        for _ in range(baud_max_count):                 # Bits transmit at each baud tick
            expected_bit = (test_bitstream >> n) & 1    # Extract nth LSB
            await RisingEdge(dut.clk)
            assert dut.TX.value == expected_bit, (
                f"expected TX = {expected_bit}, got TX = {dut.TX.value}"
            )
            assert dut.tx_ready.value == 0, (
                f"expected tx_ready = 0, got tx_ready = {dut.tx_ready.value}"   # READY should remain deasserted
            )

    # UART state should now be STOP for one bit period
    for _ in range(baud_max_count):
        await RisingEdge(dut.clk)
        assert dut.TX.value == 1, (
            f"expected TX = 1, got TX = {dut.TX.value}"
        )
        assert dut.tx_ready.value == 0, (
            f"expected tx_ready = 0, got tx_ready = {dut.tx_ready.value}"   # READY should remain deasserted
        )

    # UART state should return to IDLE, TX line held high and READY asserted
    await RisingEdge(dut.clk)
    assert dut.TX.value == 1, (
        f"expected TX = 1, got TX = {dut.TX.value}"
    )
    assert dut.tx_ready.value == 1, (
        f"expected tx_ready = 1, got tx_ready = {dut.tx_ready.value}"   # READY should now be asserted again
    )                                                                   # READY and VALID are 1 simultaneously again

    await RisingEdge(dut.clk)
    assert dut.tx_ready.value == 0, (
        f"expected tx_ready = 0, got tx_ready = {dut.tx_ready.value}"   # READY is deasserted, handshake successful
    )
    dut.tx_valid.value = 0                              # Only now deassert VALID (AXI handshake rules)

    # Now test_bitstream_2 transmission is initiating
    # UART state should be START, transitions to 0 for one bit period (period between each baud tick)
    for _ in range(baud_max_count - 1):                 # -1 because one clock cycle used for testing handshake
        await RisingEdge(dut.clk)
        assert dut.TX.value == 0, (
            f"expected TX = 0, got TX = {dut.TX.value}"
        )
        assert dut.tx_ready.value == 0, (
            f"expected tx_ready = 0, got tx_ready = {dut.tx_ready.value}"  # READY should remain deasserted
        )

    # UART state should be DATA, compare TX against data, LSB transmits first
    for n in range(data_width):
        for _ in range(baud_max_count):                 # Bits transmit at each baud tick
            expected_bit = (test_bitstream_2 >> n) & 1    # Extract nth LSB
            await RisingEdge(dut.clk)
            assert dut.TX.value == expected_bit, (
                f"expected TX = {expected_bit}, got TX = {dut.TX.value}"
            )
            assert dut.tx_ready.value == 0, (
                f"expected tx_ready = 0, got tx_ready = {dut.tx_ready.value}"   # READY should remain deasserted
            )

    # UART state should now be STOP for one bit period
    for _ in range(baud_max_count):
        await RisingEdge(dut.clk)
        assert dut.TX.value == 1, (
            f"expected TX = 1, got TX = {dut.TX.value}"
        )
        assert dut.tx_ready.value == 0, (
            f"expected tx_ready = 0, got tx_ready = {dut.tx_ready.value}"   # READY should remain deasserted
        )

    # UART state should return to IDLE, TX line held high and READY asserted
    for _ in range((data_width * baud_max_count)):  # number of clock cycles equal to data width
        await RisingEdge(dut.clk)
        assert dut.TX.value == 1, (
            f"expected TX = 1, got TX = {dut.TX.value}"
        )
        assert dut.tx_ready.value == 1, (
            f"expected tx_ready = 1, got tx_ready = {dut.tx_ready.value}"   # READY should now be asserted again
        )
