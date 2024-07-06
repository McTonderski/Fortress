package main

import (
	"context"
	"fmt"
	"os"
	"encoding/json"
	"github.com/docker/docker/client"
)

// ImageVulnerability represents a vulnerability in a Docker image
type ImageVulnerability struct {
	ID          string `json:"id"`
	Description string `json:"description"`
	Severity    string `json:"severity"`
	PackageName string `json:"package"`
	PackagePath string `json:"package_path"`
}

// ScanImage scans a Docker image for vulnerabilities
func ScanImage(imageID string) ([]ImageVulnerability, error) {
	// Create a Docker client
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return nil, err
	}

	// Get image details
	imageInspect, _, err := cli.ImageInspectWithRaw(context.Background(), imageID)
	if err != nil {
		return nil, err
	}

	// Extract vulnerabilities from image labels
	vulnerabilities := make([]ImageVulnerability, 0)
	if labels, ok := imageInspect.Config.Labels["org.opencontainers.image.vulnerabilities"]; ok {
		// Parse vulnerability information from label
		// (Assuming vulnerability information is stored as JSON in the label)
		// You may need to adjust the parsing logic based on the actual format of the label
		// For demonstration purposes, we're assuming a simple JSON format
		if err := json.Unmarshal([]byte(labels), &vulnerabilities); err != nil {
			return nil, err
		}
	}

	return vulnerabilities, nil
}

func main() {
	// Check if an image ID was provided as a command-line argument
	if len(os.Args) != 2 {
		fmt.Println("Usage: scanner <image_id>")
		os.Exit(1)
	}

	imageID := os.Args[1]

	// Scan the specified image for vulnerabilities
	vulnerabilities, err := ScanImage(imageID)
	if err != nil {
		fmt.Printf("Error scanning image %s: %v\n", imageID, err)
		os.Exit(1)
	}

	if len(vulnerabilities) > 0 {
		// Print the vulnerability report
		fmt.Printf("Vulnerabilities found in image %s:\n", imageID)
		for _, vulnerability := range vulnerabilities {
			fmt.Println(vulnerability)
		}
	} else {
		fmt.Printf("No Vulnerabilities found in image %s", imageID)
	}


	// Exit with a status code indicating the number of vulnerabilities found
	os.Exit(len(vulnerabilities))
}
