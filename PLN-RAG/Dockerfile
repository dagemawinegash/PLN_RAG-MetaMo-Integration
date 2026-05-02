# ── Stage 1: build SWI-Prolog + janus_swi from source ──────────────────────
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV SWIPL_VERSION=V9.2.9

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake ninja-build pkg-config git ca-certificates \
    python3 python3-pip python3-dev libpython3-dev \
    zlib1g-dev libssl-dev libgmp-dev libarchive-dev \
    libpcre2-dev libedit-dev libossp-uuid-dev \
    libyaml-dev libutf8proc-dev ncurses-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch ${SWIPL_VERSION} --recurse-submodules \
    https://github.com/SWI-Prolog/swipl-devel.git /tmp/swipl-devel && \
    cmake -S /tmp/swipl-devel -B /tmp/swipl-devel/build \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr/local \
      -G Ninja && \
    cmake --build /tmp/swipl-devel/build --parallel "$(nproc)" && \
    cmake --install /tmp/swipl-devel/build && \
    ldconfig && \
    swipl --version && \
    swipl --dump-runtime-variables | grep PLVERSION && \
    python3 -c 'import re, subprocess; out=subprocess.check_output(["swipl","--dump-runtime-variables"], text=True); v=int(re.search(r"PLVERSION=\"([0-9]+)\";", out).group(1)); assert v >= 90112, v'

RUN git clone https://github.com/SWI-Prolog/packages-swipy /tmp/packages-swipy && \
    cd /tmp/packages-swipy && \
    pip3 install .

# ── Stage 2: runtime image ──────────────────────────────────────────────────
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PETTA_COMMIT=e1490899cefc67c128d5311ff4861f9997674957
ENV PETTACHAINER_COMMIT=d21b93b5132a7fc8722f64d57b74fb7c3a8d1faa

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git ca-certificates \
    python3 python3-pip python3-dev libpython3-dev \
    zlib1g libssl3 libgmp10 libarchive13 \
    libpcre2-8-0 libedit2 libossp-uuid16 \
    libyaml-0-2 libutf8proc2 libncurses6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local

RUN ldconfig && \
    swipl --version && \
    swipl --dump-runtime-variables | grep PLVERSION && \
    python3 -c 'import re, subprocess; out=subprocess.check_output(["swipl","--dump-runtime-variables"], text=True); v=int(re.search(r"PLVERSION=\"([0-9]+)\";", out).group(1)); assert v >= 90112, v'

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN python3 - <<'PY'
import janus_swi as janus
print(janus.query_once("true"))
PY

# Clone PeTTa and PeTTaChainer
WORKDIR /deps
RUN git clone https://github.com/trueagi-io/PeTTa.git && \
    git -C /deps/PeTTa checkout ${PETTA_COMMIT} && \
    git clone https://github.com/rTreutlein/PeTTaChainer.git && \
    git -C /deps/PeTTaChainer checkout ${PETTACHAINER_COMMIT}

# Install PeTTa — strip the janus-swi pip dep, then point PYTHONPATH
# at the actual source dir so `import petta` resolves correctly
RUN cd /deps/PeTTa && \
    sed -i "/'janus-swi'/d" setup.py && \
    pip3 install .

ENV PYTHONPATH=/deps/PeTTa/python:$PYTHONPATH

# Install PeTTaChainer
RUN cd /deps/PeTTaChainer && \
    pip3 install -e .

# Install pln-rag app dependencies
WORKDIR /app
COPY requirements.txt .
RUN rm -rf /usr/lib/python3/dist-packages/blinker*
RUN pip3 install --default-timeout=1000 -r requirements.txt

COPY . .

VOLUME ["/app/data"]

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]