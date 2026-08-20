module uart_ascii_top
    #(
        parameter DATA_WIDTH = 8,
        parameter NUM_BYTES  = 13,
        parameter MEM_FILE   = "bitstream.mem"
    )
    (
        input logic clk,
        input logic rst,
        input logic [DATA_WIDTH-1:0] test_byte,
        input logic RX,
        output logic frame_error,
        output logic [DATA_WIDTH-1:0] data_out,
        output logic TX
    );

    // TX-side AXI-stream: axis_byte_source (master) -> uart_tx (slave)
    logic [DATA_WIDTH-1:0] tx_axis_data;
    logic tx_axis_tvalid;
    logic tx_axis_tready;
    logic tx_axis_tlast;   // unused by uart_tx, kept for completeness

    // RX-side AXI-stream: uart_rx (master) -> axis_byte_sink (slave)
    logic [DATA_WIDTH-1:0] rx_axis_data;
    logic rx_axis_tvalid;
    logic rx_axis_tready;

    // 2-FF synchroniser for RX (async input, CDC into clk domain)
    logic RX_sync_ff1, RX_sync;

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            RX_sync_ff1 <= 1'b1;
            RX_sync     <= 1'b1;
        end else begin
            RX_sync_ff1 <= RX;
            RX_sync     <= RX_sync_ff1;
        end
    end

    axis_mem_source #(
        .DATA_WIDTH(DATA_WIDTH),
        .NUM_BYTES(NUM_BYTES),
        .MEM_FILE(MEM_FILE)
    ) u_axis_mem_source (
        .clk(clk),
        .rst(rst),
        .m_axis_tdata(tx_axis_data),
        .m_axis_tvalid(tx_axis_tvalid),
        .m_axis_tlast(tx_axis_tlast),
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
        .TX(TX)
    );

    uart_rx #(
        .DATA_WIDTH(DATA_WIDTH)
    ) u_uart_rx (
        .clk(clk),
        .rst(rst),
        .RX(RX_sync),
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