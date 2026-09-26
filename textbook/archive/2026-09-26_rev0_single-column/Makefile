# make              build the book            -> main.pdf
# make chapter CH=chapters/ch02-spacetime-geometry
#                   build one chapter, cross-references kept -> chapter.pdf
# make checks       rerun the checks of worked examples (needs sympy)
# make clean        remove auxiliary files
LATEXMK ?= latexmk
NICE    ?= nice -n 10
.PHONY: book chapter checks clean
book:
	$(NICE) $(LATEXMK) main.tex
chapter:
	@test -n "$(CH)" || (echo "usage: make chapter CH=chapters/<file-without-.tex>"; exit 1)
	$(NICE) $(LATEXMK) -jobname=chapter -usepretex='\def\ChapterOnly{$(CH)}' main.tex
checks:
	$(NICE) python3 checks/ch02_ch03_examples.py | tee checks/ch02_ch03_examples.log
clean:
	$(LATEXMK) -c main.tex; $(LATEXMK) -c -jobname=chapter main.tex; find . -name '*.aux' -delete
