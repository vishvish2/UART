module uart_loop
    #(
        parameter DATA_WIDTH = 8
    )
    (
        input logic clk,
        input logic rst,
        output logic frame_error,
        output logic [DATA_WIDTH-1:0] data_out
    );

    // TX-side AXI-stream: axis_byte_source (master) -> uart_tx (slave)
    logic [DATA_WIDTH-1:0] tx_axis_data;
    logic tx_axis_tvalid;
    logic tx_axis_tready;

    // Serial wire: uart_tx -> uart_rx
    logic uart_line;

    // RX-side AXI-stream: uart_rx (master) -> axis_byte_sink (slave)
    logic [DATA_WIDTH-1:0] rx_axis_data;
    logic rx_axis_tvalid;
    logic rx_axis_tready;

    axis_byte_source #(
        .DATA_WIDTH(DATA_WIDTH)
    ) u_axis_byte_source (
        .clk(clk),
        .rst(rst),
        .data(tx_axis_data),
        .m_axis_tvalid(tx_axis_tvalid),
        .m_axis_tready(tx_axis_tready)
    );

    uart_tx #(
        .DATA_WIDTH(DATA_WIDTH)
    ) u_uart_tx (
        .clk(clk),
        .rst(rst),
        .data(tx_axis_data),
        .s_axis_tvalid(tx_axis_tvalid),
        .s_axis_tready(tx_axis_tready),
        .TX(uart_line)
    );

    uart_rx #(
        .DATA_WIDTH(DATA_WIDTH)
    ) u_uart_rx (
        .clk(clk),
        .rst(rst),
        .RX(uart_line),
        .m_axis_tready(rx_axis_tready),
        .m_axis_tvalid(rx_axis_tvalid),
        .data(rx_axis_data),
        .frame_err(frame_error)
    );

    axis_byte_sink #(
        .DATA_WIDTH(DATA_WIDTH)
    ) u_axis_byte_sink (
        .clk(clk),
        .rst(rst),
        .data(rx_axis_data),
        .s_axis_tvalid(rx_axis_tvalid),
        .s_axis_tready(rx_axis_tready),
        .data_out(data_out)
    );

endmodule