import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from enum import IntEnum

class UartState(IntEnum):
    IDLE  = 0
    START = 1
    DATA  = 2
    STOP  = 3


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
        assert dut.m_axis_tvalid.value == 0, (
            f"expected m_axis_tvalid = 0, got m_axis_tvalid = {dut.m_axis_tvalid.value}"
        )
        assert dut.data.value == 0b00000000, (
            f"expected data = 00000000, got data = {dut.data.value}"
        )
        assert dut.frame_err.value == 0, (
            f"expected frame_err = 0, got frame_err = {dut.frame_err.value}"
        )
        assert dut.curr_state.value == UartState.IDLE, (
            f"expected curr_state = {UartState.IDLE}, got curr_state = {dut.curr_state.value}"
        )

    # Simulating glitch/noise - should be ignored
    dut.RX.value = 0
    for _ in range(10):
        await RisingEdge(dut.clk)

    dut.RX.value = 1

    for _ in range(((data_width + 2) * baud_max_count)):  # number of clock cycles equal to full frame (start, data, stop)
        await RisingEdge(dut.clk)

    assert dut.curr_state.value == UartState.IDLE, (
        f"expected curr_state = {UartState.IDLE}, got curr_state = {dut.curr_state.value}"
    )

    # Start bit
    dut.RX.value = 0

    # Wait half a bit period 16x oversample -> 8 oversample baud ticks
    for _ in range(baud_max_count_oversample * 8):
        await RisingEdge(dut.clk)

    # Now uart state should be START
    assert dut.m_axis_tvalid.value == 0, (
        f"expected m_axis_tvalid = 0, got m_axis_tvalid = {dut.m_axis_tvalid.value}"
    )
    assert dut.data.value == 0b00000000, (
        f"expected data = 00000000, got data = {dut.data.value}"
    )
    assert dut.frame_err.value == 0, (
        f"expected frame_err = 0, got frame_err = {dut.frame_err.value}"
    )
    assert dut.curr_state.value == UartState.START, (
        f"expected curr_state = {UartState.START}, got curr_state = {dut.curr_state.value}"
    )

    for _ in range(baud_max_count_oversample * 8):
        await RisingEdge(dut.clk)

    # Now uart state should be DATA, but no data should be received on the RX line yet
    assert dut.m_axis_tvalid.value == 0, (
        f"expected m_axis_tvalid = 0, got m_axis_tvalid = {dut.m_axis_tvalid.value}"
    )
    assert dut.data.value == 0b00000000, (
        f"expected data = 00000000, got data = {dut.data.value}"
    )
    assert dut.frame_err.value == 0, (
        f"expected frame_err = 0, got frame_err = {dut.frame_err.value}"
    )
    assert dut.curr_state.value == UartState.DATA, (
        f"expected curr_state = {UartState.DATA}, got curr_state = {dut.curr_state.value}"
    )
    
    # Test byte to be sent on the RX line serially, LSB first
    test_bitstream = 0b01001011

    for n in range(data_width):
        for _ in range(baud_max_count):                 # Bits received at each baud tick
            RX_bit = (test_bitstream >> n) & 1          # Extract nth LSB
            dut.RX.value = RX_bit
            await RisingEdge(dut.clk)

    # After full byte is received, state should transition to STOP, RX line should be held high
    assert dut.curr_state.value == UartState.STOP, (
        f"expected curr_state = {UartState.STOP}, got curr_state = {dut.curr_state.value}"
    )
    dut.RX.value = 1

    # Value data_shift_reg should have stored the full byte
    assert dut.data_shift_reg.value == test_bitstream, (
        f"expected data_shift_reg = {test_bitstream}, got data_shift_reg = {dut.data_shift_reg.value}"
    )

    # Wait for at least half a bit period
    for _ in range(baud_max_count_oversample * 8):
            await RisingEdge(dut.clk)

    # State should still be STOP
    assert dut.curr_state.value == UartState.STOP, (
        f"expected curr_state = {UartState.STOP}, got curr_state = {dut.curr_state.value}"
    )

    # VALID should be asserted
    await RisingEdge(dut.clk)   # m_axis_tvalid gets recognised
    await RisingEdge(dut.clk)   # m_axis_tvalid updated on next rising edge
    assert dut.m_axis_tvalid.value == 1, (
        f"expected m_axis_tvalid = 1, got m_axis_tvalid = {dut.m_axis_tvalid.value}"
    )
    assert dut.frame_err.value == 0, (
        f"expected data = 0, got data = {dut.frame_err.value}"
    )

    assert dut.data.value == test_bitstream, (
        f"expected data = {test_bitstream}, got data = {dut.data.value}"
    )

    # Should return to IDLE
    assert dut.curr_state.value == UartState.IDLE, (
        f"expected curr_state = {UartState.IDLE}, got curr_state = {dut.curr_state.value}"
    )

    # Assert READY in AXI Stream interface
    dut.m_axis_tready.value = 1
    await RisingEdge(dut.clk)   # READY gets recognised
    await RisingEdge(dut.clk)   # Rising edge after handshake occurs

    # VALID should deassert after handshake
    assert dut.m_axis_tvalid_temp.value == 0, (
        f"expected m_axis_tvalid_temp = 0, got m_axis_tvalid_temp = {dut.m_axis_tvalid_temp.value}"
    )
    assert dut.m_axis_tvalid.value == 0, (
        f"expected m_axis_tvalid = 0, got m_axis_tvalid = {dut.m_axis_tvalid.value}"
    )

    # State should remain IDLE
    assert dut.curr_state.value == UartState.IDLE, (
        f"expected curr_state = {UartState.IDLE}, got curr_state = {dut.curr_state.value}"
    )
