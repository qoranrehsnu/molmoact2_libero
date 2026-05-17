#!/usr/bin/env bash
set -uo pipefail

source /home/robotics/miniconda3/etc/profile.d/conda.sh
conda activate molmoact2-libero
cd /home/robotics/molmoact2/lerobot

echo "RUN_ID=full_eval_20260515_2120"
echo "START=$(date -Is)"
echo "CWD=$(pwd)"
echo "CONDA_PREFIX=${CONDA_PREFIX}"
echo "LIBERO_CONFIG_PATH=${LIBERO_CONFIG_PATH-}"

export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export CUDA_VISIBLE_DEVICES=0
export PYTHONUNBUFFERED=1

lerobot-eval \
  --policy.type=molmoact2 \
  --policy.checkpoint_path=allenai/MolmoAct2-LIBERO \
  --policy.inference_action_mode=continuous \
  --policy.enable_cuda_graph=true \
  --policy.norm_tag=libero \
  --policy.device=cuda \
  --env.type=libero \
  --env.task=libero_10,libero_goal,libero_object,libero_spatial \
  --eval.batch_size=1 \
  --eval.n_episodes=50 \
  --seed=1000

code=$?
echo "END=$(date -Is)"
echo "EXIT_CODE=${code}"
exit "${code}"
