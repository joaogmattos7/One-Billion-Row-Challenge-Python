#!/usr/bin/env bash
# Uso: ./src/using_bash_and_awk.sh [arquivo]   (padrão: data/measurements.txt)
FILE="${1:-data/measurements.txt}"

if [ ! -f "$FILE" ]; then
    echo "Arquivo $FILE não encontrado."
    exit 1
fi

# pv (barra de progresso) é opcional
if command -v pv >/dev/null; then READ="pv -p -e -t"; else READ="cat"; fi

$READ "$FILE" | awk -F ";" \
'{
	if (!($1 in cnts)){
		mins[$1] = $2
		maxs[$1] = $2
	}
	else{
		mins[$1] = $2<mins[$1] ? $2 : mins[$1]
		maxs[$1] = $2>maxs[$1] ? $2 : maxs[$1]
	}
	cnts[$1] += 1;
	sums[$1] += $2;
} END { for (v in cnts) print v ";" maxs[v] ";" mins[v] ";" sums[v]/cnts[v] }' | sort
