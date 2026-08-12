import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def uart_rx_tb(dut):

    # 100MHz clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Data width, number of bits in the data being transmitted
    data_width = int(dut.DATA_WIDTH.value)

    # Assert reset for few clock cycles
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    assert dut.rx_valid.value == 0, (
        f"expected rx_valid = 0, got rx_valid = {dut.rx_valid.value}"
    )

    assert dut.data.value == 0b00000000, (
        f"expected data = 00000000, got data = {dut.data.value}"
    )

    assert dut.frame_err.value == 0, (
        f"expected frame_err = 0, got frame_err = {dut.frame_err.value}"
    )


    