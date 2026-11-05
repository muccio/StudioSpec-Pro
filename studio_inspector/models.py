"""
StudioSpec Pro - Data Models
Structured representations of audio devices, workstation hardware, and studio benchmark scoring.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class AudioDevice:
    id: str
    name: str
    manufacturer: str
    device_type: str  # "Input", "Output", "Duplex"
    transport: str    # "Built-in", "USB Audio", "Thunderbolt", "PCIe", "Virtual / Routing", "Dante / Network", "Bluetooth", "Aggregate"
    driver_name: str
    driver_bundle_id: str = ""
    driver_version: str = ""
    driver_type: str = "CoreAudio HAL"  # "CoreAudio HAL", "ASIO", "WASAPI Exclusive", "WDM"
    input_channels: int = 0
    output_channels: int = 0
    nominal_sample_rate: float = 48000.0
    supported_sample_rates: List[Any] = field(default_factory=list)
    buffer_size: int = 512
    min_buffer_size: int = 16
    max_buffer_size: int = 4096
    safety_offset: int = 0
    hardware_latency: int = 0
    round_trip_latency_ms: float = 0.0
    is_default_input: bool = False
    is_default_output: bool = False
    is_system_output: bool = False
    clock_source: str = "Internal Clock"
    studio_grade: str = "Standard"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CPUSpecs:
    model: str
    architecture: str
    physical_cores: int
    logical_threads: int
    performance_cores: int = 0
    efficiency_cores: int = 0
    base_clock_mhz: float = 0.0
    boost_clock_mhz: float = 0.0
    simd_features: List[str] = field(default_factory=list)
    thermal_throttling: str = "Normal / Full Performance"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RAMSpecs:
    total_gb: float
    available_gb: float
    memory_type: str
    swap_used_mb: float = 0.0
    swap_pressure: str = "Low / Optimal"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class StorageSpecs:
    primary_drive_name: str
    medium_type: str  # "NVMe SSD (Apple Fabric)", "NVMe M.2 SSD", "SATA SSD", "HDD"
    total_gb: float
    free_gb: float
    free_percentage: float
    estimated_speed_mbs: float
    dfd_streaming_readiness: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DiskBenchmarkResult:
    mount_point: str
    write_speed_mbs: float
    seq_read_speed_mbs: float
    rnd_read_speed_mbs: float
    rnd_iops: int
    effective_dfd_bandwidth_mbs: float
    max_voices_48k: int
    max_voices_96k: int
    patches_heavy_48k: int
    patches_standard_48k: int
    patches_light_48k: int
    patches_heavy_96k: int
    patches_standard_96k: int
    assessment: str
    click_risk: str
    recommended_kontakt_dfd_buffer: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class OSSpecs:
    os_name: str
    os_version: str
    kernel: str
    audio_subsystem: str
    power_plan: str
    audio_daemon_status: str
    plugin_formats_supported: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DAWReadinessProfile:
    use_case: str
    rating: str  # "Eccellente", "Ottimo", "Buono", "Limitato", "Non Consigliato"
    score_pct: int
    comment: str

@dataclass
class BenchmarkScore:
    total_score: int  # 0 to 100
    tier: str
    tier_badge: str
    tier_description: str
    audio_io_score: float      # max 30
    cpu_dsp_score: float       # max 30
    ram_sample_score: float    # max 25
    storage_dfd_score: float   # max 15
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    daw_readiness: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class StudioWorkstationReport:
    timestamp: str
    hostname: str
    platform: str
    cpu: CPUSpecs
    ram: RAMSpecs
    storage: StorageSpecs
    os_info: OSSpecs
    audio_devices: List[AudioDevice]
    score: BenchmarkScore
    disk_benchmark: Optional[DiskBenchmarkResult] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "hostname": self.hostname,
            "platform": self.platform,
            "cpu": self.cpu.to_dict(),
            "ram": self.ram.to_dict(),
            "storage": self.storage.to_dict(),
            "os_info": self.os_info.to_dict(),
            "audio_devices": [dev.to_dict() for dev in self.audio_devices],
            "score": self.score.to_dict(),
            "disk_benchmark": self.disk_benchmark.to_dict() if self.disk_benchmark else None
        }
