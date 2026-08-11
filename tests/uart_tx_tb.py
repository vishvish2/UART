import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def uart_tx_tb(dut):

    # 100MHz clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Assert reset for few clock cycles
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    # UART state should be IDLE and assert READY in AXI interface
    await RisingEdge(dut.clk)
    assert dut.tx_ready.value == 1

    # In IDLE, TX line should be held high
    for _ in range(8):
        await RisingEdge(dut.clk)
        assert dut.TX.value == 1
