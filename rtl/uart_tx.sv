module uart_tx
    #(
        parameter CLK_FREQ = 100000000,
        parameter BAUD_RATE = 115200,
        parameter DATA_WIDTH = 8
    )
    (
        input logic clk,
        input logic rst,
        input logic [DATA_WIDTH-1:0] data,
        input logic s_axis_tvalid,
        output logic s_axis_tready,
        output logic TX
    );

// Temporary values
logic [DATA_WIDTH-1:0] tx_data_temp;
logic tx_temp = 1'b0;

// UART states
typedef enum {IDLE, START, DATA, STOP}  uart_state;

uart_state curr_state = IDLE;
uart_state next_state = IDLE;

// Counter for baud clock
localparam BAUD_MAX_COUNT = CLK_FREQ/BAUD_RATE;
localparam BAUD_COUNT_SIZE = $clog2(BAUD_MAX_COUNT);

// Baud values
logic [BAUD_COUNT_SIZE-1:0] baud_count;
logic baud_tick;

// Counter for data
localparam DATA_COUNT_SIZE = $clog2(DATA_WIDTH);

// Data values
logic [DATA_COUNT_SIZE-1:0] data_count;
logic end_data;

// Shift register for storing data to transmit
logic [DATA_WIDTH-1:0] data_shift_reg;

// AXI Stream Interface
always_ff @(posedge clk)
    begin
        if (rst) begin
            tx_data_temp <= '0;
        end

        else begin
            if (s_axis_tvalid & s_axis_tready) begin
                tx_data_temp <= data;
            end
        end
    end

// Baud Clock
always @(posedge clk)
    begin
        if (rst)
            baud_count <= '0;
        else if (curr_state == IDLE && next_state == START)
            baud_count <= '0;
        else if (baud_tick)
            baud_count <= '0;
        else
            baud_count <= baud_count + 'd1;
    end

// Baud tick condition
assign baud_tick = (baud_count == BAUD_MAX_COUNT-1) ? 1'b1 : 1'b0;

always @(posedge clk)
    begin
        if (rst) begin
            data_count <= '0;
            data_shift_reg <= '0;
        end

        else if (baud_tick) begin
            // Reset data_count and update data_shift_reg on state transition
            if (curr_state != next_state) begin
                data_count <= '0;
                data_shift_reg <= tx_data_temp;
            end

            else begin
                // Shift the shift register
                data_count <= data_count + 'd1;
                data_shift_reg <= data_shift_reg >> 1;
            end
        end
    end

assign end_data = (data_count == DATA_WIDTH-1) ? 1'b1 : 1'b0;

always @(*)
    begin
        case (curr_state)
            IDLE:
                begin
                    if (s_axis_tvalid) begin
                        next_state = START;
                    end

                    else begin
                        next_state = curr_state;
                    end
                    tx_temp = 1'b1;     // Hold tx line high when idle
                end

            START:
                begin
                    if (baud_tick) begin
                        next_state = DATA;
                    end

                    else begin
                        next_state = curr_state;
                    end
                    tx_temp = 1'b0;     // Pull tx line low for one baud period to indicate start
            end

            DATA:
                begin
                    if (end_data & baud_tick) begin
                        next_state = STOP;
                    end

                    else begin
                        next_state = curr_state;
                    end
                    tx_temp = data_shift_reg[0];    // Transmit LSB of data_shift_reg
                end

            STOP:
                begin
                    if (baud_tick) begin
                        next_state = IDLE;
                    end

                    else begin
                        next_state = curr_state;
                    end
                    tx_temp = 1'b1;
                end

            default:
                begin
                    next_state = curr_state;
                    tx_temp = 1'b1;
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

assign s_axis_tready = (curr_state == IDLE) ? 1'b1 : 1'b0;
assign TX = tx_temp;

endmodule
