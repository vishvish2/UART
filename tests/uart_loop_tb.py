import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def uart_loop_tb(dut):

    # 100MHz clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Data width, number of bits in the data being transmitted
    data_width = int(dut.DATA_WIDTH.value)

    # Baud count max value to keep track of baud ticks
    baud_max_count = int(dut.u_uart_tx.BAUD_MAX_COUNT.value)

    # Assert reset for few clock cycles
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    lsfr_val = 0b11111111

    for _ in range(256):
        await RisingEdge(dut.clk)

        # 8-bit lfsr to generate 8-bit values in pseudorandom order
        feedback = (                    # XOR 8th, 6th, 5th and 4th bits
            ((lsfr_val >> 7) & 1)
            ^ ((lsfr_val >> 5) & 1)
            ^ ((lsfr_val >> 4) & 1)
            ^ ((lsfr_val >> 3) & 1)
        )

        lsfr_val = ((lsfr_val << 1) & 0xFF) | feedback  # Shift and add feedback bit to LSB
        expected_data_out = lsfr_val
        dut.test_byte.value = expected_data_out

        # Let uart run for a number of clock cycle required for a full frame to transmit
        for _ in range(((data_width + 2) * baud_max_count)):    # start bit, 8 bit data, stop bit = 10 baud ticks
            await RisingEdge(dut.clk)

        assert dut.data_out.value == expected_data_out, (
            f"expected data_out = {expected_data_out}, got data_out = {dut.data_out.value}"
        )
