using Microsoft.Azure.CognitiveServices.ContentModerator;
using Microsoft.CognitiveServices.ContentModerator;
using Microsoft.CognitiveServices.ContentModerator.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;

namespace TextModeration
{
    class Program
    {

        // The name of the file that contains the text to evaluate.
        private static string TextFile = "TextFile.txt";

        // The name of the file to contain the output from the evaluation.
        private static string OutputFile = "TextModerationOutput.txt";
        
        static void Main(string[] args)
        {
            // Load the input text.
            string text = File.ReadAllText(TextFile);
            Console.WriteLine("Screening {0}", TextFile);

            text = text.Replace(System.Environment.NewLine, " ");
            byte[] byteArray = System.Text.Encoding.UTF8.GetBytes(text);
            MemoryStream stream = new MemoryStream(byteArray);

            // Save the moderation results to a file.
            using (StreamWriter outputWriter = new StreamWriter(OutputFile, false))
            {
                // Create a Content Moderator client and evaluate the text.
                using (var client = Clients.NewClient())
                {
                    // Screen the input text: check for profanity,
                    // autocorrect text, check for personally identifying
                    // information (PII), and classify the text into three categories
                    outputWriter.WriteLine("Autocorrect typos, check for matching terms, PII, and classify.");
                    var screenResult =
                    client.TextModeration.ScreenText("text/plain", stream, "eng", true, true, null, true);
                    outputWriter.WriteLine(
                            JsonConvert.SerializeObject(screenResult, Formatting.Indented));
                }
                outputWriter.Flush();
                outputWriter.Close();
            }

        }

    }

    // Wraps the creation and configuration of a Content Moderator client.
    public static class Clients
    {
        // The region/location for your Content Moderator account, 
        // for example, westus.
        private static readonly string AzureRegion = "YOUR API REGION";

        // The base URL fragment for Content Moderator calls.
        private static readonly string AzureBaseURL =
            $"https://{AzureRegion}.api.cognitive.microsoft.com";

        // Your Content Moderator subscription key.
        private static readonly string CMSubscriptionKey = "YOUR API KEY";

        // Returns a new Content Moderator client for your subscription.
        public static ContentModeratorClient NewClient()
        {
            // Create and initialize an instance of the Content Moderator API wrapper.
            ContentModeratorClient client = new ContentModeratorClient(new ApiKeyServiceClientCredentials(CMSubscriptionKey));

            client.Endpoint = AzureBaseURL;
            return client;
        }
    }
}