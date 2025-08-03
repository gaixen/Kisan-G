import os
import base64
import logging
import json
from typing import TypedDict, List, Any
from PIL import Image
import cv2
# from snippets.prompt import build_prompt
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class AgentState(TypedDict):
    """
    Defines the state that flows through our agent. It's a dictionary that
    holds all the intermediate data as the agent works on a problem.
    """
    initial_query: str
    media_path: str
    disease_name: str
    initial_analysis: str
    remedy_search_results: str
    final_report: str

class CropDiseaseAnalyzer:
    """
    An agentic class that uses a multimodal model and web search to analyze
    crop diseases and recommend remedies. This class encapsulates the entire
    LangGraph pipeline.
    """
    def __init__(self):
        """
        Initializes the agent, setting up the AI model, tools, and compiling
        the analysis workflow (graph).
        """
        self.model = ChatGoogleGenerativeAI(model="gemma-3n", temperature=0.2)
        self.search_tool = TavilySearchResults(max_results=4)
        self.graph = self._build_graph()

    # --- Private Helper Methods for Media Processing ---

    def _encode_image(self, image_path: str) -> str:
        """Encodes an image file to a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _process_video_to_frames(self, video_path: str, max_frames: int = 10) -> List[str]:
        """Extracts a set number of frames from a video and encodes them."""
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0
        while cap.isOpened() and frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            encoded_frame = base64.b64encode(buffer).decode('utf-8')
            frames.append(encoded_frame)
            frame_count += 1
        cap.release()
        return frames

    # --- LangGraph Nodes: The Steps in our Pipeline ---

    def analyze_media_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Analyzes the user's media (image/video/text) to make an initial diagnosis.
        """
        logger.info("---AGENT STEP: Analyzing Media---")
        query = state['initial_query']
        media_path = state['media_path']
        
        prompt = f"""
You are an expert agricultural botanist. Analyze the provided media and the user's query to identify the plant and any visible diseases or pests.

User's description: "{query}"

1.  **Identify the Plant**: Determine the type of crop.
2.  **Analyze Symptoms**: Describe the symptoms you observe in detail.
3.  **Initial Diagnosis**: State the most likely disease, pest, or deficiency. If the plant appears healthy, clearly state that.

Provide a concise summary of your findings, and on a new line, write the common name of the disease ONLY (e.g., "Powdery Mildew", "Black Spot", "Aphid Infestation", "Healthy"). This name will be used for web searches.
"""
        
        message_content : list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        
        if media_path and os.path.exists(media_path):
            file_ext = media_path.lower().split('.')[-1]
            if file_ext in ['png', 'jpg', 'jpeg']:
                encoded_image = self._encode_image(media_path)
                message_content.append({
                    "type": "image_url", 
                    "text": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                })
            elif file_ext in ['mp4', 'mov', 'avi']:
                encoded_frames = self._process_video_to_frames(media_path)
                for frame in encoded_frames:
                    message_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}})

        response = self.model.invoke([HumanMessage(content=message_content)])
        
        # Split the response to get the full analysis and the clean disease name
        parts = response.content.strip().split('\n')
        initial_analysis = "\n".join(parts[:-1])
        disease_name = parts[-1].strip()
        
        logger.info(f"Initial Diagnosis: {disease_name}")
        return {**state, "initial_analysis": initial_analysis, "disease_name": disease_name}

    def search_for_remedies_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Uses the disease name from the previous step to search the web for remedies.
        """
        logger.info("---AGENT STEP: Searching for Remedies---")
        disease_name = state['disease_name']
        if not disease_name or disease_name.lower() == "healthy":
            # Return the full AgentState with only remedy_search_results updated
            return {**state, "remedy_search_results": "No remedies needed as the plant appears healthy."}
            
        search_query = f"remedies and treatments for {disease_name} on plants"
        remedy_results = self.search_tool.invoke(search_query)
        logger.info(f"Found {len(remedy_results)} search results.")
        return {**state, "remedy_search_results": json.dumps(remedy_results, indent=2)}

    def compile_final_report_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Synthesizes the initial analysis and web search results into a final, user-friendly report.
        """
        logger.info("---AGENT STEP: Compiling Final Report---")
        report_prompt = f"""
You are an expert agricultural assistant, writing a report for a concerned farmer or gardener.
Combine your initial expert analysis with the provided web search results to create a comprehensive and actionable guide.

**Your Initial Analysis:**
{state['initial_analysis']}

**Web Search Results for Remedies:**
{state['remedy_search_results']}

**Task:**
Create a final report in Markdown format with the following sections:
- **Diagnosis**: Clearly state the final diagnosis.
- **Key Symptoms**: List the symptoms that led to this diagnosis.
- **Recommended Actions**: Provide a clear, step-by-step guide for treatment. Include both organic and chemical options if the search results provide them.
- **Prevention Tips**: Offer advice on how to prevent this issue in the future.
"""
        
        final_report_response = self.model.invoke([HumanMessage(content=report_prompt)])
        logger.info("Final report generated.")
        return {**state, "final_report": final_report_response.content}

    def _build_graph(self):
        """
        Builds the LangGraph agentic workflow.
        """
        workflow = StateGraph(AgentState)
        # Add the nodes (the functions to call)
        workflow.add_node("analyze_media", self.analyze_media_node)
        workflow.add_node("search_for_remedies", self.search_for_remedies_node)
        workflow.add_node("compile_final_report", self.compile_final_report_node)

        # Define the edges (the order of operations)
        workflow.set_entry_point("analyze_media")
        workflow.add_edge("analyze_media", "search_for_remedies")
        workflow.add_edge("search_for_remedies", "compile_final_report")
        workflow.add_edge("compile_final_report", END)

        # Compile the graph into a runnable application
        return workflow.compile()

    # --- Public-Facing Method ---

    def analyze_crop(self, media_path: str, query: str) -> dict:
        """
        The main public method to run the crop analysis pipeline.

        Args:
            media_path (str): The file path to the image or video of the crop.
            query (str): The user's text description of the issue.

        Returns:
            dict: The final report from the agent.
        """
        logger.info(f"Starting new crop analysis for: {media_path}")
        initial_state = {
            "initial_query": query,
            "media_path": media_path,
        }
        
        # The `stream` method runs the graph from start to finish
        final_state = self.graph.invoke(initial_state)
        
        return final_state


# --- Example Usage ---
if __name__ == '__main__':
    # This block demonstrates how to use the CropDiseaseAnalyzer class.
    
    # 1. Create an instance of the analyzer
    analyzer = CropDiseaseAnalyzer()

    # 2. Create a dummy image file for demonstration
    # In a real application, this path would come from a file upload.
    dummy_image_path = r"C:\Users\sudip\gemma-3n-impact\remote\backend\tests\__results___23_2.png"
    try:
        # Create a simple, blank white image using the Pillow library
        img = Image.new('RGB', (200, 200), color = 'white')
        img.save(dummy_image_path)
        print(f"Created a dummy image at: '{dummy_image_path}' for the demo.")
        print("NOTE: The AI is powerful, but will perform best with a REAL image of a plant.\n")

        # 3. Define the user's query
        user_query = "My tomato plant's leaves are developing these yellow spots and seem to be curling. What could it be?"

        # 4. Run the analysis pipeline
        # The `analyze_crop` method handles the entire multi-step process.
        final_result = analyzer.analyze_crop(media_path=dummy_image_path, query=user_query)

        # 5. Print the final, user-friendly report
        print("\n" + "="*50)
        print("          Final Crop Analysis Report")
        print("="*50 + "\n")
        if final_result.get("final_report"):
            print(final_result["final_report"])
        else:
            print("Could not generate a final report. Check logs for errors.")
            print("\nFull final state:")
            print(json.dumps(final_result, indent=2))

    except Exception as e:
        logger.error(f"An error occurred in the main execution block: {e}", exc_info=True)
    
    finally:
        # 6. Clean up the dummy file
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)
            print(f"\nCleaned up dummy file: '{dummy_image_path}'")
        
        print("\n--- Script finished ---")