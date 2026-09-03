<?php

use Phalcon\Mvc\Controller;

class SearchController extends Controller
{
    public function indexAction()
    {
        $keyword = $this->request->getPost('keyword', 'string');
        if ($keyword) {
            // Call Rust Command Engine via HTTP for unified search
            $engineUrl = getenv('RUST_ENGINE_URL') ?: 'http://rust-engine:8090/command';
            
            $context = stream_context_create([
                'http' => [
                    'method' => 'POST',
                    'header' => "Content-Type: application/json\r\n",
                    'content' => json_encode(['command' => 'search ' . $keyword]),
                    'timeout' => 10
                ]
            ]);
            
            $result = @file_get_contents($engineUrl, false, $context);
            if ($result !== false) {
                $response = json_decode($result, true);
                $this->view->results = $response['output'] ?? $result;
            } else {
                // Fallback: try local command-engine binary
                $cmd = '/usr/local/bin/command-engine search ' . escapeshellarg($keyword);
                $this->view->results = shell_exec($cmd);
            }
            $this->view->keyword = $keyword;
        }
    }
}
