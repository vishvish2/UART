# UART Controller

This repository contains system verilog code for transmitting and receiving UART frames the following properties.
- 1 start bit
- 8-bit data width
- 1 stop bit
- No parity bit
- 115200 baud rate

The data width and baud rate can be customised by modifying the parameters in the modules in `rtl/`

The code was synthesised in Vivado and could successfully interact with an ESP32-C3 supermini's UART interface which runs on the arduino code in `arduino/uart_test.ino`.

The memory file `bitstream.mem` has the ASCII values for "hello world" with a carriage return and new line.

## HDL Files

Folder `rtl/` contains the system verilog code
- `rtl/uart_tx` is code for the UART transmitter
- `rtl/uart_rx` is code for the UART receiver
- `rtl/axis_byte_source` is code to send data to `rtl/uart_tx` to transmit
- `rtl/axis_byte_sink` is code to receive data from `rtl/uart_rx`

All the above modules have an AXI-Stream interface.

The module `rtl/uart_loop` combines the above modules, connecting the TX line from `rtl/uart_tx` to the RX line of `rtl/uart_rx`.

The module `rtl/uart_top` also combines the above modules, but instead sends the TX line to an output port and receiving an RX line from an input port.
- The TX line transmits 8 bit data can be connected to any on board DIP switches.
- The RX line receives 8 bit data and can be connected to any on board LEDs.

The module `rtl/uart_ascii_top`, again, also combines the above modules, but instead reads ASCII values from a memory file and sends them to the TX line connected to an output port and receives an RX line from an input port.
- The RX line receives 8 bit data and can be connected to any on board LEDs.

## Testbenches

Folder `tests/` contains testbenches written in python using the cocotb library.

In order to run the testbenches, open the project in an IDE of your choice and navigate to the tests directory in a terminal via `cd tests`.

Below are the commands for running each test benches.
```text
make tx         # Runs uart_tx_tb.py
make rx         # Runs uart_rx_tb.py
make loop       # Runs uart_loop_tb.py
make run_all    # Runs all of the above
```

## Vivado FPGA Implementation

The FPGA used is the Artix-7 Nexys A7 board with part number xc7a100tcsg324-1

Below is Vivado's timing analysis with a 100MHz clock input with the expected HDL file hierarchies.

Where `rtl/uart_loop.sv` is the top level module:
![uart_loop_timing](img/uart_loop_vivado_timing.png)
![uart_loop_hierarchy](img/uart_loop_hierarchy.png)

Where `rtl/uart_top.sv` is the top level module:
![uart_top_timing](img/uart_top_vivado_timing.png)
![uart_top_hierarchy](img/uart_top_hierarchy.png)

Where `rtl/uart_ascii_top.sv` is the top level module:
![uart_ascii_top_timing](img/uart_ascii_top_vivado_timing.png)
![uart_ascii_top_hierarchy](img/uart_ascii_top_hierarchy.png)