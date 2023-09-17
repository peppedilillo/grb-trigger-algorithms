inputs=data/simulated_dataset_compeff
outputs=computational_efficiency/outputs

mkdir -p $outputs > /dev/null 2>&1
echo "created output folder"
echo "deleting old outputs file."
rm $outputs/*.txt

outfile_gbm="results_gbm.txt";
outfile_focus="results_focus.txt";
printf "\nNew test: computational performances\n"
echo "----Running algorithms----"
for filename in "$inputs"/*.txt; do
  echo "running gbm on $filename"
  echo "$filename" >> "$outputs"/"$outfile_gbm";
  ./algorithms_c/benchmark/cmake-build-release/gbm_benchmark "$filename" >> "$outputs"/"$outfile_gbm";
  echo "running focus on $filename"
  echo "$filename" >> "$outputs"/"$outfile_focus";
  ./algorithms_c/pfocus_c/cmake-build-release/pfocus_compeff "$filename" >> "$outputs"/"$outfile_focus";
done

cd computational_efficiency || exit
tables="tables";
outfile_table="table.txt";
mkdir -p $tables > /dev/null 2>&1
echo "created table folder"
echo "deleting old tables."
rm "$tables"/"$outfile_table"

python table.py > "$tables"/"$outfile_table";
cd ..

echo "Done."
