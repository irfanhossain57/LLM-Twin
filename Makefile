.PHONY: etl features dataset train eval serve

etl:
	python -m data_collection.dispatcher

features:
	python -m feature_pipeline.cdc

dataset:
	python -m training_pipeline.generate_instruct_dataset

train:
	python -m training_pipeline.finetune

eval:
	python -m evaluation.llm_judge

serve:
	python -m inference_pipeline.llm_twin_service
