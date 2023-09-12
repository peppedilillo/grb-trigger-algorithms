inputs=./inputs
outputs=./outputs

mkdir -p $outputs > /dev/null 2>&1
echo "created output folder"
rm $outputs/*.txt
echo "deleted old outputs file."

outfile_gbm="results_gbm.txt";
outfile_focus="results_focus.txt";
printf "\nNew test: computational performances\n"
echo "----Running algorithms----"
for filename in "$inputs"/*.txt; do
  echo "running gbm on $filename"
  echo "$filename" >> "$outputs"/"$outfile_gbm";
  ./algorithms_c/benchmark_c/cmake-build-release/gbm_benchmark "$filename" >> "$outputs"/"$outfile_gbm";
  echo "running focus on $filename"
  echo "$filename" >> "$outputs"/"$outfile_focus";
  ./algorithms_c/pfocus_c/cmake-build-release/pfocus_compeff "$filename" >> "$outputs"/"$outfile_focus";
done

printf "\nDone.\n"
