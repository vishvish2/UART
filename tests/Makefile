SIM            ?= icarus
TOPLEVEL_LANG  ?= verilog

VERILOG_SOURCES += $(PWD)/../rtl/uart_tx.sv
VERILOG_SOURCES += $(PWD)/../rtl/uart_rx.sv
VERILOG_SOURCES += $(PWD)/../rtl/axis_byte_source.sv
VERILOG_SOURCES += $(PWD)/../rtl/axis_byte_sink.sv
VERILOG_SOURCES += $(PWD)/../rtl/uart_loop.sv

COMPILE_ARGS += -g2012

all: tx rx loop
tx:
	$(MAKE) sim COCOTB_TEST_MODULES=uart_tx_tb COCOTB_TOPLEVEL=uart_tx
	rm -rf sim_build
	rm results.xml

rx:
	$(MAKE) sim COCOTB_TEST_MODULES=uart_rx_tb COCOTB_TOPLEVEL=uart_rx
	rm -rf sim_build
	rm results.xml

loop:
	$(MAKE) sim COCOTB_TEST_MODULES=uart_loop_tb COCOTB_TOPLEVEL=uart_loop
	rm -rf sim_build
	rm results.xml

include $(shell cocotb-config --makefiles)/Makefile.sim
