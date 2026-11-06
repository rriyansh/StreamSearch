## StreamSearch: Real-Time Multimodal Video Search.

StreamSearch is a high-throughput video analytics engine designed to perform real-time, natural-language semantic searches across live video streams. By heavily optimizing vision-language models with hardware acceleration and combining them with specialized vector databases, StreamSearch achieves sub-50ms query latency while ingesting video at a sustained 30 FPS.

### Key Features.

Zero-Shot Multimodal Search: Search live video using natural language without pre-tagging or bounding boxes.

Ultra-Low Latency: End-to-end query retrieval in under 50 milliseconds.

High-Throughput Ingestion: Sustained 30 Frames Per Second (FPS) processing per camera stream, buffered safely via event streaming.

Hardware Accelerated: Utilizes NVIDIA TensorRT for optimized FP16/INT8 inference, drastically reducing the compute footprint of heavy vision models.

Scalable Vector Retrieval: Leverages Qdrant Approximate Nearest Neighbor (ANN) indexing for instantaneous semantic matching.

## System Architecture.

The pipeline is decoupled into microservices to ensure stability under heavy loads:

Live Video Stream (RTSP/WebRTC): Raw video frames are captured from target sources.

Apache Kafka (Ingestion Queue): Acts as a shock absorber. Frames are serialized and pushed to Kafka topics, decoupling ingestion from inference and preventing frame drops during traffic spikes.

CLIP Model (Vision-Language): Frames are consumed and processed by the CLIP model to generate high-dimensional vector embeddings of the visual scene.

TensorRT & CUDA (Acceleration): The CLIP vision encoder is compiled with TensorRT, maximizing GPU utilization through layer fusion and precision calibration for real-time throughput.

Qdrant (ANN Index): Embeddings are streamed directly into Qdrant for rapid similarity indexing.

Instant Timestamp Result: User text queries are embedded and compared against the Qdrant index using cosine similarity, returning the exact timestamp of the matching frame.

### Tech Stack.

Message Broker: Apache Kafka

AI/ML Model: OpenAI CLIP (ViT-B/32 or ViT-L/14)

Hardware Acceleration: NVIDIA CUDA toolkit, TensorRT

Vector Database: Qdrant

Backend / API: Python, FastAPI

Deployment: Docker, Docker Compose

## Prerequisites.

To run StreamSearch, your environment must meet the following requirements:

OS: Linux (Ubuntu 22.04 recommended)

GPU: NVIDIA GPU with at least 8GB VRAM (e.g., RTX 3080, A10G, T4)

Drivers: NVIDIA Driver >= 530.xx, CUDA Toolkit 12.1+

Software: Docker, Docker Compose, Python 3.10+

### Installation and Setup.

1. Clone the repository

git clone https://github.com/your-org/StreamSearch.git
cd StreamSearch


2. Configure Environment Variables

Copy the template and adjust your settings for RTSP stream URLs and GPU allocations.

cp .env.example .env


3. Build the TensorRT Engine

Before starting the pipeline, compile the CLIP model weights to a TensorRT engine optimized for your specific GPU architecture.

python scripts/build_trt_engine.py --model ViT-B/32 --precision fp16


4. Start the Infrastructure

Launch Kafka and Qdrant using Docker Compose.

docker-compose up -d zookeeper kafka qdrant


5. Launch the StreamSearch Pipeline

Start the worker nodes and API server.

docker-compose up --build ingestion-worker inference-worker api-server


### Usage.

Once the pipeline is running, the API will be available at http://localhost:8000.

Submitting a Search Query

You can query the live stream using a simple REST API call.

Request:

curl -X POST "http://localhost:8000/api/v1/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "a person riding a bicycle", "time_window": "last_10_mins", "limit": 3}'


Response:

{
  "query": "a person riding a bicycle",
  "latency_ms": 38,
  "results": [
    {
      "timestamp": "2023-10-27T14:32:01.450Z",
      "stream_id": "camera_front_gate",
      "confidence_score": 0.89
    }
  ]
}


### Performance Benchmarks.

Tested on an NVIDIA RTX 4090, Intel i9-13900K, Ubuntu 22.04

Metric

Measurement

Notes

Ingestion Rate

30 FPS

Zero frame drops via Kafka buffering

Inference Time (CLIP + TRT)

~12ms / frame

FP16 precision

Vector Indexing (Qdrant)

< 5ms

Batched gRPC inserts

End-to-End Query Latency

< 50ms

Text embedding + ANN Search + JSON return

### Roadmap.

[ ] Multi-camera distributed scaling via Kubernetes.

[ ] Support for open-source alternatives to CLIP (e.g., BLIP-2, SigLIP).

[ ] Web-based user interface with live bounding-box highlighting.

[ ] INT8 quantization for edge-device deployment (Jetson Orin).

### Contributing.

We welcome contributions. Please read the contributing guidelines for details on our code of conduct and the process for submitting pull requests.

### License.

This project is licensed under the MIT License. See the license file for details.
