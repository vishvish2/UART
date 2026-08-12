SIM            ?= icarus
TOPLEVEL_LANG  ?= verilog

VERILOG_SOURCES += $(PWD)/../rtl/uart_tx.sv
VERILOG_SOURCES += $(PWD)/../rtl/uart_rx.sv

COMPILE_ARGS += -g2012

tx:
	$(MAKE) sim COCOTB_TEST_MODULES=uart_tx_tb COCOTB_TOPLEVEL=uart_tx
	rm -rf sim_build
	rm results.xml

rx:
	$(MAKE) sim COCOTB_TEST_MODULES=uart_rx_tb COCOTB_TOPLEVEL=uart_rx
	rm -rf sim_build
	rm results.xml

include $(shell cocotb-config --makefiles)/Makefile.sim
