module axis_byte_source
    #(
        parameter DATA_WIDTH = 8
    )
    (
        input logic clk,
        input logic rst,
        input logic [DATA_WIDTH-1:0] test_byte,
        output logic [DATA_WIDTH-1:0] data,
        output logic m_axis_tvalid,
        input logic m_axis_tready
    );

    // Temporary values
    logic m_axis_tvalid_temp;

    // Always has valid data for simplicity for testing
    assign data = test_byte;
    assign m_axis_tvalid_temp = 1'b1;

    // AXI Stream Interface
    always_ff @(posedge clk)
        if (rst)
            m_axis_tvalid <= 0;
        
        else if (!m_axis_tvalid || m_axis_tready) begin
            m_axis_tvalid <= m_axis_tvalid_temp;
        end

endmodule
