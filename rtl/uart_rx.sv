module uart_rx
    #(
        parameter CLK_FREQ = 100000000,
        parameter BAUD_RATE = 115200,
        parameter DATA_WIDTH = 8
    )
    (
        input logic clk,
        input logic rst,
        input logic RX,
        input logic m_axis_tready,
        output logic m_axis_tvalid,
        output logic [DATA_WIDTH-1:0] data,
        output logic frame_err
    );

// Temporary values
logic m_axis_tvalid_temp;

// UART states
typedef enum {IDLE, START, DATA, STOP}  uart_state;

uart_state curr_state = IDLE;
uart_state next_state = IDLE;

// Counters for baud clock
localparam BAUD_MAX_COUNT = CLK_FREQ/BAUD_RATE;
localparam BAUD_COUNT_SIZE = $clog2(BAUD_MAX_COUNT);

// 16x oversample baud clock
localparam BAUD_MAX_COUNT_OVERSAMPLE = CLK_FREQ/(BAUD_RATE * 16);
localparam BAUD_COUNT_SIZE_OVERSAMPLE = $clog2(BAUD_MAX_COUNT_OVERSAMPLE);

// Baud values
logic [BAUD_COUNT_SIZE_OVERSAMPLE-1:0] baud_count_oversample;
logic baud_tick_oversample;

// Counter for data
localparam DATA_COUNT_SIZE = $clog2(DATA_WIDTH);

// Data values
logic [DATA_COUNT_SIZE-1:0] data_count;
logic end_data;

// Shift register for storing received data
logic [DATA_WIDTH-1:0] data_shift_reg;

// AXI Stream interface
always_ff @(posedge clk)
    begin
        if (rst) begin
            m_axis_tvalid <= 0;
        end

        else if (!m_axis_tvalid || m_axis_tready) begin
            m_axis_tvalid <= m_axis_tvalid_temp;
        end
    end

always_ff @(posedge clk)
    begin
        if (!m_axis_tvalid || m_axis_tready)
            data <= data_shift_reg;
    end

// Baud Clock
always @(posedge clk)
    begin
        if (rst)
            baud_count_oversample <= '0;
        else if (curr_state == IDLE && next_state == START)
            baud_count_oversample <= '0;
        else if (baud_tick_oversample)
            baud_count_oversample <= '0;
        else
            baud_count_oversample <= baud_count_oversample + 'd1;
    end

// Baud tick condition
assign baud_tick_oversample = (baud_count_oversample == BAUD_MAX_COUNT_OVERSAMPLE-1) ? 1'b1 : 1'b0;

// Position within the current bit period, counted in oversample ticks
logic [3:0] oversample_tick_count;  // 0-15 needs 4 bits
logic bit_midpoint;                 // midpoint of a potential bit
logic baud_tick;                    // baud tick at normal rate

always @(posedge clk)
    begin
        if (rst)
            oversample_tick_count <= '0;
        else if (curr_state == IDLE && next_state == START)
            oversample_tick_count <= '0;
        else if (baud_tick_oversample) begin
            if (baud_tick)
                oversample_tick_count <= '0;
            else
                oversample_tick_count <= oversample_tick_count + 'd1;
        end
    end

assign bit_midpoint = baud_tick_oversample && (oversample_tick_count == 4'd7);
assign baud_tick = baud_tick_oversample && (oversample_tick_count == 4'd15);

always @(posedge clk)
    begin
        if (rst) begin
            data_count <= '0;
            data_shift_reg <= '0;
        end

        else if (curr_state == START && next_state == DATA) begin
            data_count <= '0;
        end

        else if (curr_state == DATA && bit_midpoint) begin
            data_count <= data_count + 'd1;
            data_shift_reg <= {RX, data_shift_reg[DATA_WIDTH-1:1]};
        end
    end

assign end_data = (data_count == DATA_WIDTH-1) ? 1'b1 : 1'b0;

always @(*)
    begin
        case (curr_state)
            IDLE:
                begin
                    if (RX == 1'b1) begin
                        next_state = curr_state;
                    end
                    
                    else begin
                        next_state = START;
                    end
                    m_axis_tvalid_temp = 1'b0;
                    frame_err = 1'b0;
                end

            START:
                begin
                    if (bit_midpoint) begin
                        if (RX == 1'b0)
                            next_state = DATA;  // Confirmed start bit

                        else
                            next_state = IDLE;  // Just noise, ignore
                    end

                    else begin
                        next_state = curr_state;
                    end
                    m_axis_tvalid_temp = 1'b0;
                    frame_err = 1'b0;
                end

            DATA:
                begin
                    if (end_data & bit_midpoint) begin
                        next_state = STOP;
                    end

                    else begin
                        next_state = curr_state;
                    end
                    m_axis_tvalid_temp = 1'b0;
                    frame_err = 1'b0;
                end

            STOP:
                begin
                    if (bit_midpoint) begin
                        if (RX == 1'b1) begin
                            frame_err = 1'b0;
                            m_axis_tvalid_temp = 1'b1;
                        end

                        else begin
                            frame_err = 1'b1;
                            m_axis_tvalid_temp = 1'b0;   // Frame error, stop bit not constant 1
                        end
                        next_state = IDLE;
                    end

                    else begin
                        next_state = curr_state;
                        frame_err = 1'b0;
                        m_axis_tvalid_temp = 1'b0;
                    end
                end

            default: 
                begin
                    next_state = curr_state;
                    frame_err = 1'b0;
                    m_axis_tvalid_temp = 1'b0;
                end                
        endcase    
    end

always @(posedge clk)
    begin
        if (rst) begin
            curr_state <= IDLE;
        end

        else begin
            curr_state <= next_state;
        end

    end

endmodule