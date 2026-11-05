"""
StudioSpec Pro - Audio Buffer & Round-Trip Latency Calculator
Calculates exact real-time input, output, and round-trip latencies (RTL) across various
sample rates and buffer sizes, providing studio tracking recommendations.
"""

from typing import Dict, Any, List

def calculate_latency(
    sample_rate: float,
    buffer_size: int,
    safety_offset: int = 64,
    hardware_latency: int = 64
) -> Dict[str, Any]:
    """Calculate input, output, and round-trip latency in milliseconds."""
    if sample_rate <= 0:
        sample_rate = 48000.0

    one_way_buffer_ms = (buffer_size / sample_rate) * 1000.0
    half_hw_safe = (safety_offset + hardware_latency) / 2.0
    
    input_latency_ms = ((buffer_size + half_hw_safe) / sample_rate) * 1000.0
    output_latency_ms = ((buffer_size + half_hw_safe) / sample_rate) * 1000.0
    round_trip_ms = input_latency_ms + output_latency_ms

    if round_trip_ms < 3.5:
        suitability = "Imperceptible / Real-Time IEM Vocal & Guitar Tracking"
        suitability_class = "success"
    elif round_trip_ms < 6.5:
        suitability = "Optimal / Virtual Instruments & MIDI Performance"
        suitability_class = "success"
    elif round_trip_ms < 12.0:
        suitability = "Standard / Acceptable for Overdubs & Comping"
        suitability_class = "warning"
    else:
        suitability = "High Latency / Mixing, Mastering & DSP Heavy Sessions"
        suitability_class = "danger"

    return {
        "sample_rate_hz": sample_rate,
        "buffer_size_samples": buffer_size,
        "one_way_buffer_ms": round(one_way_buffer_ms, 2),
        "input_latency_ms": round(input_latency_ms, 2),
        "output_latency_ms": round(output_latency_ms, 2),
        "round_trip_latency_ms": round(round_trip_ms, 2),
        "suitability": suitability,
        "suitability_class": suitability_class
    }

def get_latency_matrix(
    sample_rates: List[int] = [44100, 48000, 96000, 192000],
    buffers: List[int] = [32, 64, 128, 256, 512, 1024]
) -> List[Dict[str, Any]]:
    """Generate a studio buffer matrix for reference."""
    matrix = []
    for sr in sample_rates:
        for b in buffers:
            matrix.append(calculate_latency(sr, b))
    return matrix
