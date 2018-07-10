for n in {1..5000}; do
    dd if=/dev/urandom of=artifacts/file$( printf %03d "$n" ).bin bs=1 count=$(( `shuf -i 500-2200 -n 1` + 1024 ))
done