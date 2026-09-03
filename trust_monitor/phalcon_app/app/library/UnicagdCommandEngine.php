<?php
/**
 * UNICAGD Command Engine - PHP Wrapper
 * 
 * Provides PHP interface to the Rust command engine.
 * Supports CLI, JSON, and HTTP modes.
 */

class UnicagdCommandEngine
{
    private string $enginePath;
    private ?string $projectRoot;
    private ?string $httpEndpoint;
    
    public function __construct(string $enginePath = null, string $projectRoot = null)
    {
        $this->enginePath = $enginePath ?? '/usr/local/bin/command-engine';
        $this->projectRoot = $projectRoot ?? getcwd();
        $this->httpEndpoint = null;
    }
    
    /**
     * Set HTTP endpoint for remote engine
     */
    public function setHttpEndpoint(string $url): void
    {
        $this->httpEndpoint = rtrim($url, '/');
    }
    
    /**
     * Execute a command and return result
     */
    public function execute(string $command): array
    {
        if ($this->httpEndpoint) {
            return $this->executeHttp($command);
        }
        return $this->executeCli($command);
    }
    
    /**
     * Execute via CLI
     */
    private function executeCli(string $command): array
    {
        $descriptors = [
            0 => ['pipe', 'r'],
            1 => ['pipe', 'w'],
            2 => ['pipe', 'w']
        ];
        
        $cmd = sprintf(
            '%s execute %s',
            escapeshellcmd($this->enginePath),
            escapeshellarg($command)
        );
        
        $process = proc_open($cmd, $descriptors, $pipes, $this->projectRoot);
        
        if (!is_resource($process)) {
            return [
                'success' => false,
                'output' => '',
                'error' => 'Failed to start command engine process',
                'exit_code' => -1
            ];
        }
        
        // Close stdin
        fclose($pipes[0]);
        
        // Read stdout and stderr
        $stdout = stream_get_contents($pipes[1]);
        fclose($pipes[1]);
        
        $stderr = stream_get_contents($pipes[2]);
        fclose($pipes[2]);
        
        $exitCode = proc_close($process);
        
        return [
            'success' => $exitCode === 0,
            'output' => trim($stdout),
            'error' => trim($stderr),
            'exit_code' => $exitCode
        ];
    }
    
    /**
     * Execute via HTTP
     */
    private function executeHttp(string $command): array
    {
        $url = $this->httpEndpoint . '/command';
        $data = json_encode(['command' => $command]);
        
        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => "Content-Type: application/json\r\n",
                'content' => $data,
                'timeout' => 30
            ]
        ]);
        
        $result = @file_get_contents($url, false, $context);
        
        if ($result === false) {
            return [
                'success' => false,
                'output' => '',
                'error' => 'HTTP request failed: ' . $url,
                'exit_code' => -1
            ];
        }
        
        $response = json_decode($result, true);
        
        return [
            'success' => $response['success'] ?? false,
            'output' => $response['output'] ?? '',
            'error' => $response['error'] ?? '',
            'exit_code' => $response['exit_code'] ?? 0
        ];
    }
    
    /**
     * Run audit
     */
    public function audit(): array
    {
        return $this->execute('audit');
    }
    
    /**
     * Show manifest with optional filter
     */
    public function manifest(string $filter = null): array
    {
        $cmd = $filter !== null ? "manifest {$filter}" : 'manifest';
        return $this->execute($cmd);
    }
    
    /**
     * Show LSTM state
     */
    public function lstm(): array
    {
        return $this->execute('lstm');
    }
    
    /**
     * Show exokernel state
     */
    public function exokernel(): array
    {
        return $this->execute('exokernel');
    }
    
    /**
     * Search data model
     */
    public function search(string $query): array
    {
        return $this->execute("search {$query}");
    }
    
    /**
     * Show system status
     */
    public function status(): array
    {
        return $this->execute('status');
    }
    
    /**
     * Execute arbitrary system command
     */
    public function system(string $command): array
    {
        return $this->execute("execute {$command}");
    }
    
    /**
     * Check if engine is available
     */
    public function isAvailable(): bool
    {
        if ($this->httpEndpoint) {
            return true; // Assume available if endpoint set
        }
        
        return file_exists($this->enginePath) && is_executable($this->enginePath);
    }
    
    /**
     * Get engine version/info
     */
    public function info(): array
    {
        return $this->execute('status');
    }
}

// Usage example in Phalcon controller:
// $engine = new UnicagdCommandEngine();
// $result = $engine->search('kernel');
// echo $result['output'];
