use dns_lookup::{lookup_host, lookup_txt};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

/// DNS-derived feature vector for LSTM training optimization.
#[derive(Debug, Clone)]
pub struct DnsFeatureVector {
    pub domain: String,
    pub ip_count: usize,
    pub avg_ttl: f64,
    pub has_mx: bool,
    pub txt_count: usize,
    pub nameserver_depth: usize,
    pub entropy: f64,
    pub timestamp: u64,
}

impl DnsFeatureVector {
    pub fn dimensionality() -> usize {
        8
    }

    pub fn to_lstm_input(&self) -> Vec<f64> {
        let mut vec = [0.0; 8];
        vec[0] = (self.ip_count as f64).ln().max(0.0);
        vec[1] = self.avg_ttl / 86400.0;
        vec[2] = if self.has_mx { 1.0 } else { 0.0 };
        vec[3] = (self.txt_count as f64).ln().max(0.0);
        vec[4] = (self.nameserver_depth as f64).ln().max(0.0);
        vec[5] = self.entropy;
        vec[6] = (self.timestamp % 86400) as f64 / 86400.0;
        vec[7] = (self.timestamp % 604800) as f64 / 60480.0;
        vec.to_vec()
    }
}

/// Segment classifier for grouping domains into LSTM training batches.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum TrainingSegment {
    Tld(String),
    NameserverCluster(String),
    RegistrarBucket(u8),
    TemporalWindow(u8),
}

/// DNS-LSTM optimizer: uses DNS hierarchy to create training segments.
pub struct DnsLstmOptimizer {
    cache: HashMap<String, DnsFeatureVector>,
    segment_counts: HashMap<TrainingSegment, usize>,
}

impl DnsLstmOptimizer {
    pub fn new() -> Self {
        Self {
            cache: HashMap::new(),
            segment_counts: HashMap::new(),
        }
    }

    /// Resolve domain and extract features.
    pub fn resolve_domain(&mut self, domain: &str) -> Option<DnsFeatureVector> {
        if let Some(cached) = self.cache.get(domain) {
            return Some(cached.clone());
        }

        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        let mut feature = DnsFeatureVector {
            domain: domain.to_string(),
            ip_count: 0,
            avg_ttl: 0.0,
            has_mx: false,
            txt_count: 0,
            nameserver_depth: 0,
            entropy: 0.0,
            timestamp,
        };

        match lookup_host(domain) {
            Ok(ips) => {
                feature.ip_count = ips.len();
                let entropy_input: Vec<u8> = ips.iter().flat_map(|ip| ip.octets()).collect();
                feature.entropy = Self::byte_entropy(&entropy_input);
            }
            Err(_) => {}
        }

        match lookup_txt(domain) {
            Ok(txts) => {
                feature.txt_count = txts.len();
            }
            Err(_) => {}
        }

        feature.has_mx = Self::probe_mx(domain).unwrap_or(false);

        let parts: Vec<&str> = domain.split('.').collect();
        feature.nameserver_depth = parts.len();

        let feature_clone = feature.clone();
        self.cache.insert(domain.to_string(), feature_clone);
        Some(feature)
    }

    /// Classify domain into training segment.
    pub fn classify_segment(&self, domain: &str) -> TrainingSegment {
        let parts: Vec<&str> = domain.split('.').collect();
        if parts.len() >= 2 {
            let tld = parts.last().copied().unwrap_or("");
            return TrainingSegment::Tld(tld.to_string());
        }
        TrainingSegment::Tld("unknown".to_string())
    }

    /// Assign domain to segment and return batch recommendation.
    pub fn assign_training_batch(&mut self, domain: &str) -> Option<usize> {
        let segment = self.classify_segment(domain);
        let count = self.segment_counts.entry(segment).or_insert(0);
        let batch_id = *count;
        *count += 1;
        Some(batch_id)
    }

    /// Get cached feature vector.
    pub fn get_feature(&self, domain: &str) -> Option<&DnsFeatureVector> {
        self.cache.get(domain)
    }

    /// Batch resolve multiple domains.
    pub fn batch_resolve(&mut self, domains: &[String]) -> Vec<DnsFeatureVector> {
        domains
            .iter()
            .filter_map(|d| self.resolve_domain(d))
            .collect()
    }

    /// Compute Shannon entropy of byte slice.
    fn byte_entropy(data: &[u8]) -> f64 {
        if data.is_empty() {
            return 0.0;
        }
        let mut counts = [0usize; 256];
        for &b in data {
            counts[b as usize] += 1;
        }
        let len = data.len() as f64;
        let mut entropy = 0.0;
        for &c in &counts {
            if c > 0 {
                let p = c as f64 / len;
                entropy -= p * p.log2();
            }
        }
        entropy
    }

    /// Stub MX probe.
    fn probe_mx(_domain: &str) -> Option<bool> {
        None
    }
}

impl Default for DnsLstmOptimizer {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_feature_vector_dimension() {
        assert_eq!(DnsFeatureVector::dimensionality(), 8);
    }

    #[test]
    fn test_segment_classification() {
        let opt = DnsLstmOptimizer::new();
        let seg = opt.classify_segment("example.com");
        match seg {
            TrainingSegment::Tld(tld) => assert_eq!(tld, "com"),
            _ => panic!("Expected Tld segment"),
        }
    }

    #[test]
    fn test_byte_entropy() {
        let data = b"aaaa";
        let entropy = DnsLstmOptimizer::byte_entropy(data);
        assert!(entropy < 0.1);
    }
}
