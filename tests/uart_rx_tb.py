import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def uart_rx_tb(dut):

    # 100MHz clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Data width, number of bits in the data being transmitted
    data_width = int(dut.DATA_WIDTH.value)

    # Baud count max value to keep track of baud ticks
    baud_max_count_oversample = int(dut.BAUD_MAX_COUNT_OVERSAMPLE.value)
    baud_max_count = baud_max_count_oversample * 16

    # Assert reset for few clock cycles
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    # Line held high in IDLE
    dut.RX.value = 1

    # UART state should be IDLE
    # VALID should be deasserted, data should default to zeros with no frame error flag
    for _ in range(((data_width + 2) * baud_max_count)):  # number of clock cycles equal to full frame (start, data, stop)
        await RisingEdge(dut.clk)
        assert dut.rx_valid.value == 0, (
            f"expected rx_valid = 0, got rx_valid = {dut.rx_valid.value}"
        )

        assert dut.data.value == 0b00000000, (
            f"expected data = 00000000, got data = {dut.data.value}"
        )

        assert dut.frame_err.value == 0, (
            f"expected frame_err = 0, got frame_err = {dut.frame_err.value}"
        )

    # Simulating glitch/noise - should be ignored
    dut.RX.value = 0
    for _ in range(10):
        await RisingEdge(dut.clk)

    dut.RX.value = 1

    for _ in range(((data_width + 2) * baud_max_count)):  # number of clock cycles equal to full frame (start, data, stop)
            await RisingEdge(dut.clk)
            assert dut.rx_valid.value == 0, (
                f"expected rx_valid = 0, got rx_valid = {dut.rx_valid.value}"
            )
    
            assert dut.data.value == 0b00000000, (
                f"expected data = 00000000, got data = {dut.data.value}"
            )
    
            assert dut.frame_err.value == 0, (
                f"expected frame_err = 0, got frame_err = {dut.frame_err.value}"
            )
    