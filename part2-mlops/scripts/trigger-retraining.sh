#!/bin/bash
# Trigger re-training pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

MODE=${1:-drift}
REFERENCE_DATE=${2:-"2024-01-14"}
CURRENT_DATE=${3:-$(date +%Y-%m-%d)}
NODE_ID=${4:-"hospital_01"}

echo "🔄 Triggering re-training pipeline..."
echo "   Mode: $MODE"
echo "   Reference Date: $REFERENCE_DATE"
echo "   Current Date: $CURRENT_DATE"
echo "   Node ID: $NODE_ID"

cd "$PROJECT_ROOT"

if [ "$MODE" == "drift" ]; then
    python part2-mlops/mlops/retraining_pipeline.py \
        --mode drift \
        --reference-date "$REFERENCE_DATE" \
        --current-date "$CURRENT_DATE" \
        --node-id "$NODE_ID"
elif [ "$MODE" == "scheduled" ]; then
    python part2-mlops/mlops/retraining_pipeline.py \
        --mode scheduled
else
    echo "❌ Unknown mode: $MODE"
    echo "   Use 'drift' or 'scheduled'"
    exit 1
fi

echo "✅ Re-training pipeline completed!"

