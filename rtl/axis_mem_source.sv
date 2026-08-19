module axis_mem_source
    #(
        parameter DATA_WIDTH = 8,
        parameter NUM_BYTES  = 13,
        parameter MEM_FILE   = "bitstream.mem"
    )
    (
        input  logic clk,
        input  logic rst,

        output logic [DATA_WIDTH-1:0] m_axis_tdata,
        output logic                  m_axis_tvalid,
        output logic                  m_axis_tlast,
        input  logic                  m_axis_tready
    );

    localparam IDX_W = (NUM_BYTES > 1) ? $clog2(NUM_BYTES) : 1;

    logic [DATA_WIDTH-1:0] mem [0:NUM_BYTES-1];

    initial begin
        $readmemb(MEM_FILE, mem);
    end

    logic [IDX_W-1:0] addr_q;

    wire handshake = m_axis_tvalid & m_axis_tready;
    wire last_byte = (addr_q == NUM_BYTES-1);

    // Address of the NEXT byte to present, wrapping around
    wire [IDX_W-1:0] next_addr = last_byte ? '0 : addr_q + 1'b1;

    always_ff @(posedge clk) begin
        if (rst) begin
            addr_q        <= '0;
            m_axis_tdata  <= mem[0];
            m_axis_tvalid <= 1'b1;          // always has data to send
            m_axis_tlast  <= (NUM_BYTES == 1);
        end
        else if (handshake) begin
            addr_q        <= next_addr;
            m_axis_tdata  <= mem[next_addr];
            m_axis_tlast  <= (next_addr == NUM_BYTES-1);
        end
    end

endmodule