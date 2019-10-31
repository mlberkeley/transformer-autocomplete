#!/bin/bash
# Training Script

python run_lm_finetuning.py --output_dir=output --model_type=gpt2 --model_name_or_path=gpt2 --do_train --train_data_file="./train_data.txt" --do_eval --eval_data_file="./test_data.txt" --per_gpu_train_batch_size 2 --per_gpu_eval_batch_size 2 #--overwrite_output_dir