from langchain_core.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

conversation = """
Person A: Hey, excuse me, is this seat taken? The keynote on DeFi scalability was packed!
Person B: Oh, hey! No, go for it. I'm Alex, by the way. Yeah, that was a great talk.
Person A: I'm Jamie. Nice to meet you, Alex. So, what brings you to CryptoCon? Are you deep in the DeFi space too?
Person B: You could say that! I'm a smart contract developer for a project focused on decentralized identity solutions. We're trying to make it easier for users to control their own data using blockchain. How about you, Jamie?
Person A: That's fascinating! I'm on the other side of the coin, so to speak. I'm a market analyst for a crypto research firm. I spend my days tracking trends, tokenomics, and trying to predict the next big wave. So, less building, more observing.
Person B: Ah, a market guru! We definitely need more people like you to make sense of all this chaos. It's interesting, your analysis probably informs the kind of projects that get traction, which then impacts what developers like me build.
Person A: Exactly! It's all interconnected. I've been particularly interested in the intersection of NFTs and real-world asset tokenization lately. Seems like a huge potential area.
Person B: Totally agree. We've actually been exploring how decentralized identity could play a role in verifying ownership of tokenized assets. Makes the whole process more secure and transparent.
Person A: That's a great point. We should definitely connect. I'd love to hear more about your project and how DID can be applied there. Maybe we could grab a coffee tomorrow morning before the sessions start?
Person B: Sounds like a plan, Jamie. I'm free around 8:30. Let's exchange contact info. Here's my LinkedIn QR code.
Person A: Perfect. Just scanned it. I'll send you a message. Looking forward to it!
"""

if __name__ == "__main__":
    load_dotenv()
    print("Starting LangChain...")

    summary_template = """
    Given the coversation {conversation}, I want you to do the following:
    1. Identify the name of the person who is speaking if mentioned.
    2. Identify the job title, description, role, or industry of the person if mentioned.
    3. Identify any other relevant contact information such as email, phone number, birthday, or social media handles if mentioned.
    4. Summarize the conversation in a concise manner.
    5. Provide a list of key points discussed in the conversation.
    6. Provide a list of actionable items or next steps that were agreed upon during the conversation.
    """

    summary_prompt_template = PromptTemplate(
        input_variables=["conversation"], template=summary_template
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        google_api_key=os.environ.get("GEMINI_API_KEY"),
    )

    chain = summary_prompt_template | llm

    res = chain.invoke(input={"conversation": conversation})
    print(res)
