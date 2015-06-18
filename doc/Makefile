SOURCES=progProcess.dot         \
	progProcessInDetail.dot \
	typesOfBugs.dot
TARGETS=$(subst .dot,.png,$(SOURCES)) $(subst .dot,.svg,$(SOURCES))

all: $(TARGETS)

%.svg: %.dot
	dot -Tsvg $< -o $@

%.png: %.dot
	dot -Tpng $< -o $@
