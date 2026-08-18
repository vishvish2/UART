module axis_byte_sink
    #(
        parameter DATA_WIDTH = 8
    )
    (
        input logic clk,
        input logic rst,
        input logic [DATA_WIDTH-1:0] data,
        input logic s_axis_tvalid,
        output logic s_axis_tready,
        output logic [DATA_WIDTH-1:0] data_out
    );

    // Always ready to accept, for simplicity of testing
    always_ff @(posedge clk)
        if (rst)
            s_axis_tready <= 1'b0;
        else
            s_axis_tready <= 1'b1;
  
    always_ff @(posedge clk) begin
        if (rst)
            data_out <= '0;
        else if (s_axis_tvalid && s_axis_tready)
            data_out <= data;
    end
endmodule