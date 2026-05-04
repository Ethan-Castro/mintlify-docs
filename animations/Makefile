.PHONY: all install manim matplotlib interactives clean

PYTHON ?= .venv/bin/python
MANIM  ?= .venv/bin/manim
Q      ?= m
VIDEO_DIR     := ../images/videos
INTERACT_DIR  := ../images/interactives

MANIM_SCENES = \
  manim/slurm_job_lifecycle.py:SlurmJobLifecycle \
  manim/mpi_job_distribution.py:MPIJobDistribution \
  manim/storage_io_flow.py:StorageIOFlow \
  manim/globus_transfer.py:GlobusTransfer \
  manim/openmp_fork_join.py:OpenMPForkJoin \
  manim/hybrid_mpi_openmp.py:HybridMPIOpenMP \
  manim/distributed_dl_training.py:DistributedDLTraining

all: manim matplotlib interactives

install:
	uv venv .venv 2>/dev/null || python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

manim:
	@mkdir -p $(VIDEO_DIR)
	@for entry in $(MANIM_SCENES); do \
		file=$${entry%%:*}; scene=$${entry##*:}; out=$$(basename $$file .py).mp4; \
		echo ">>> rendering $$scene from $$file"; \
		$(MANIM) -q$(Q) --media_dir media -o $$out $$file $$scene || exit 1; \
	done
	@find media/videos -name '*.mp4' -exec cp {} $(VIDEO_DIR)/ \;
	@echo ">>> Manim outputs copied to $(VIDEO_DIR)"

matplotlib:
	@mkdir -p $(VIDEO_DIR)
	$(PYTHON) matplotlib/gpu_utilization_heatmap.py $(VIDEO_DIR)/gpu_utilization_heatmap.mp4

interactives:
	@mkdir -p $(INTERACT_DIR)
	cp threejs/empire_ai_architecture.html       $(INTERACT_DIR)/
	cp d3/empire_ai_research_domains.html        $(INTERACT_DIR)/

clean:
	rm -rf media
