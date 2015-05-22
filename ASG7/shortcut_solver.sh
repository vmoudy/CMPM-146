./gringo $@ \
    | ./reify \
    | ./clingo --parallel-mode=4 --outf=2 \
            - \
            metaS.lp \
            ./meta*.lp 2>/dev/null