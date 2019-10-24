// <snippet_using>
using Microsoft.Azure.CognitiveServices.ContentModerator;
using Microsoft.Azure.CognitiveServices.ContentModerator.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
// </snippet_using>

namespace ImageModeration
{
    class Program
    {
        static void Main(string[] args)
        {
            // <snippet_main>
            // Create an object to store the image moderation results.
            List<EvaluationData> evaluationData = new List<EvaluationData>();

            // Create an instance of the Content Moderator API wrapper.
            using (var client = Clients.NewClient())
            {
                // Read image URLs from the input file and evaluate each one.
                using (StreamReader inputReader = new StreamReader(ImageUrlFile))
                {
                    while (!inputReader.EndOfStream)
                    {
                        string line = inputReader.ReadLine().Trim();
                        if (line != String.Empty)
                        {
                            EvaluationData imageData = EvaluateImage(client, line);
                            evaluationData.Add(imageData);
                        }
                    }
                }
            }

            // Save the moderation results to a file.
            using (StreamWriter outputWriter = new StreamWriter(OutputFile, false))
            {
                outputWriter.WriteLine(JsonConvert.SerializeObject(
                    evaluationData, Formatting.Indented));

                outputWriter.Flush();
                outputWriter.Close();
            }
            // </snippet_main>
        }

        // <snippet_fields>
        //The name of the file that contains the image URLs to evaluate.
        private static string ImageUrlFile = "ImageFiles.txt";

        ///The name of the file to contain the output from the evaluation.
        private static string OutputFile = "ModerationOutput.json";
        // </snippet_fields>

        // <snippet_evaluate>
        // Evaluates an image using the Image Moderation APIs.
        private static EvaluationData EvaluateImage(
          ContentModeratorClient client, string imageUrl)
        {
            var url = new BodyModel("URL", imageUrl.Trim());

            var imageData = new EvaluationData();

            imageData.ImageUrl = url.Value;

            // Evaluate for adult and racy content.
            imageData.ImageModeration =
                client.ImageModeration.EvaluateUrlInput("application/json", url, true);
            Thread.Sleep(1000);

            // Detect and extract text.
            imageData.TextDetection =
                client.ImageModeration.OCRUrlInput("eng", "application/json", url, true);
            Thread.Sleep(1000);

            // Detect faces.
            imageData.FaceDetection =
                client.ImageModeration.FindFacesUrlInput("application/json", url, true);
            Thread.Sleep(1000);

            return imageData;
        }
        // </snippet_evaluate>
    }

    // <snippet_client>
    // Wraps the creation and configuration of a Content Moderator client.
    public static class Clients
    {
        // The base URL fragment for Content Moderator calls.
        // Add your Azure Content Moderator endpoint to your environment variables.
        private static readonly string AzureBaseURL =
            Environment.GetEnvironmentVariable("FACE_ENDPOINT");

        // Your Content Moderator subscription key.
        // Add your Azure Content Moderator subscription key to your environment variables.
        private static readonly string CMSubscriptionKey = 
            Environment.GetEnvironmentVariable("CONTENT_MODERATOR_SUBSCRIPTION_KEY");

        // Returns a new Content Moderator client for your subscription.
        public static ContentModeratorClient NewClient()
        {
            // Create and initialize an instance of the Content Moderator API wrapper.
            ContentModeratorClient client = new ContentModeratorClient(new ApiKeyServiceClientCredentials(CMSubscriptionKey));

            client.Endpoint = AzureBaseURL;
            return client;
        }
    }
    // </snippet_client>

    // <snippet_dataclass>
    // Contains the image moderation results for an image, 
    // including text and face detection results.
    public class EvaluationData
    {
        // The URL of the evaluated image.
        public string ImageUrl;

        // The image moderation results.
        public Evaluate ImageModeration;

        // The text detection results.
        public OCR TextDetection;

        // The face detection results;
        public FoundFaces FaceDetection;
    }
    // </snippet_dataclass>
}
