SIM            ?= icarus
TOPLEVEL_LANG  ?= verilog

VERILOG_SOURCES += $(PWD)/../rtl/uart_tx.sv

COMPILE_ARGS += -g2012

tx:
	$(MAKE) sim COCOTB_TEST_MODULES=uart_tx_tb COCOTB_TOPLEVEL=uart_tx

include $(shell cocotb-config --makefiles)/Makefile.sim
