module axis_byte_source
    #(
        parameter DATA_WIDTH = 8
    )
    (
        input logic clk,
        input logic rst,
        output logic [DATA_WIDTH-1:0] data,
        output logic m_axis_tvalid,
        input logic m_axis_tready
    );

    logic m_axis_tvalid_temp;
    logic [DATA_WIDTH-1:0] test_byte;

    // Hard coded test byte for simplicity
    assign test_byte = 8'b01001010;
    assign data = test_byte;

    // Always has valid data for simplicity for testing
    assign m_axis_tvalid_temp = 1'b1;

    // AXI Stream Interface
    always_ff @(posedge clk)
        if (rst)
            m_axis_tvalid <= 0;
        
        else if (!m_axis_tvalid || m_axis_tready) begin
            m_axis_tvalid <= m_axis_tvalid_temp;
        end

endmodule
