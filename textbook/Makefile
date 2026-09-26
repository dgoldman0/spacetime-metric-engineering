# make              build the figures, then the book    -> main.pdf
# make figures      rebuild changed figures (figures/src/*.tex -> figures/*.pdf)
# make chapter CH=chapters/ch02-spacetime-geometry
#                   build one chapter, cross-references kept -> chapter.pdf
# make checks       rerun the checks of worked examples and quoted numbers
# make clean        remove auxiliary files
LATEXMK ?= latexmk
NICE    ?= nice -n 10
FIGSRC  := $(filter-out figures/src/figpreamble.tex,$(wildcard figures/src/*.tex))
FIGPDF  := $(patsubst figures/src/%.tex,figures/%.pdf,$(FIGSRC))
.PHONY: book figures chapter checks clean
book: figures
	$(NICE) $(LATEXMK) main.tex
figures: $(FIGPDF)
figures/%.pdf: figures/src/%.tex figures/src/figpreamble.tex preamble/colors.tex
	@mkdir -p figures/build
	cd figures/src && extra_mem_top=30000000 extra_mem_bot=30000000 $(NICE) pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../build $*.tex > /dev/null || (tail -25 ../build/$*.log; exit 1)
	cp figures/build/$*.pdf $@
chapter: figures
	@test -n "$(CH)" || (echo "usage: make chapter CH=chapters/<file-without-.tex>"; exit 1)
	$(NICE) $(LATEXMK) -jobname=chapter -usepretex='\def\ChapterOnly{$(CH)}' main.tex
checks:
	$(NICE) python3 checks/ch02_ch03_examples.py | tee checks/ch02_ch03_examples.log
	$(NICE) python3 checks/rev1_quoted_numbers.py | tee checks/rev1_quoted_numbers.log
	$(NICE) python3 checks/rev2_teaching_devices.py | tee checks/rev2_teaching_devices.log
clean:
	$(LATEXMK) -c main.tex; $(LATEXMK) -c -jobname=chapter main.tex; find . -name '*.aux' -delete; rm -rf figures/build
