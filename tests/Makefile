SIM            ?= icarus
TOPLEVEL_LANG  ?= verilog

VERILOG_SOURCES += $(PWD)/../rtl/uart_tx.sv
VERILOG_SOURCES += $(PWD)/../rtl/uart_rx.sv

COMPILE_ARGS += -g2012

tx:
	$(MAKE) sim COCOTB_TEST_MODULES=uart_tx_tb COCOTB_TOPLEVEL=uart_tx

rx:
	$(MAKE) sim COCOTB_TEST_MODULES=uart_rx_tb COCOTB_TOPLEVEL=uart_rx

include $(shell cocotb-config --makefiles)/Makefile.sim
