# UART Controller

This repository contains system verilog code for a UART controller with the following properties.
- 1 start bit
- 8-bit data width
- 1 stop bit
- No parity bit
- 115200 baud

The data width and baud rate can be customised by modifying the parameters in the modules in `rtl/`

## Files

Folder `rtl/` contains the system verilog code
- `rtl/uart_tx` is code for the UART transmitter
- `rtl/uart_rx` is code for the UART receiver
- `rtl/axis_byte_source` is code to send data to `rtl/uart_tx` to transmit
- `rtl/axis_byte_sink` is code to receive data from `rtl/uart_rx`

All the above modules have an AXI-Stream interface.

The module `rtl/uart_loop` combines the above modules, connecting the TX line from `rtl/uart_tx` to the RX line of `rtl/uart_rx`.

## Vivado FPGA Implentation

Below is Vivado's timing analysis with a 100MHz clock input where `rtl/uart_loop.sv` is the top level module.
![Timing](img/uart_loop_vivado_timing.png "Timing")