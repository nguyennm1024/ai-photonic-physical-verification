"""
AI Prompts for Photonics Layout Verification
=============================================

⚠️ CRITICAL WARNING ⚠️
DO NOT MODIFY THESE PROMPTS WITHOUT EXTENSIVE TESTING!

These prompts are precisely tuned for photonic waveguide discontinuity detection.
Any changes may significantly impact analysis accuracy.

The prompts were originally developed and tested in layout_verification_app.py
and are copied here EXACTLY as they were.
"""

# =============================================================================
# DISCONTINUITY ANALYSIS PROMPT
# =============================================================================
# This is the main prompt used by Gemini Pro (gemini-2.5-pro) for detailed
# discontinuity analysis of photonic waveguide tiles.
#
# EXACT COPY from layout_verification_app.py line 1445-1479
# =============================================================================

DISCONTINUITY_ANALYSIS_PROMPT = """
You are a photonics layout verification expert. Given a cropped image of a photonic integrated circuit (PIC) layout block, your task is to detect and explain any discontinuities in waveguide structures.
📌 Context:
The image is cropped from a larger layout, so cut-off shapes at the image border are not considered discontinuities.

🚨 CRITICAL FIRST STEP - IDENTIFY ACTUAL WAVEGUIDES:
Before analyzing for discontinuities, you MUST first determine if this image contains actual waveguides:
- If you see only repetitive grid patterns, + (plus) shapes, ▭ rectangles, or regular background structures with no clear channel/gap patterns, then there are NO waveguides to analyze → report "continuity"
- Waveguides are hollow channels/gaps between colored material boundaries where light travels
- Background grid elements are NOT waveguides and should be completely ignored
- Only proceed with discontinuity analysis if you can clearly identify actual waveguide channels

In this image:
The colored shapes (e.g., teal) represent drawn material (e.g., silicon).
The waveguide is the entire hollow region between these colored boundaries, where light is guided — this could be white or any other color. However, you must to discriminate waveguide with background.
The waveguide must be relatively smooth and continuous. If there is a mismatch between two connectors, then it is potentially discontinuity. However, if the mismatch appears to be due to a resolution issue, then it is okay, meaning if the other segments are smooth but suddenly one segment is mismatched, then that is the problem.
Tapering is not a discontinuity, meaning that the waveguide tapering smoothly is not a problem. 
🔍 Your Tasks:
Focus on the geometric shape and alignment of the waveguide region (remember to discriminate waveguide with background) — i.e., the gap between the colored boundaries that forms the optical channel.
Do not just check if the area is unbroken. Instead, assess if the waveguide:
Shows any offset, step, or misalignment across tiles or segments. Some misalignment is intentional in design, so if you're sure it's because of design, it's not discontinuity.
Has a sudden change in width or slope, and it's not because of design.
Breaks its smooth curvature or continuity, even if the space looks connected, especially in the connector area.
If you detect a discontinuity:
Describe it clearly (e.g., "step offset in the lower boundary at center", or "break in alignment across stitched tiles")
Remember, it's unacceptable to miss any non-smoothness, if any non-smoothness is found, it's a discontinuity.
If the waveguide is fully continuous and smoothly aligned (no non-smoothness, even smallest found), say so explicitly — but only after verifying smoothness in both shape and position. 
⚠️ Critical Warning:
Do not assume the presence of space means continuity. A slight step or misalignment in shape — even if small — may cause significant optical discontinuity.
Your judgment must focus on geometric alignment and smooth shape continuity, not just presence of empty space.
You must focus on what you can see, do not imagine, assume, or hallucinate.
You must discriminate waveguide and background, they could be the same color, but they are different.
The + (plus, sometime look like T because of crop) and ▭ (rectangle, sometimes look like U or reversed U due to crop) are background, not waveguide, you must ignore them, you must just focus on the waveguide.
Background is not discontinuity.
"""

# =============================================================================
# CLASSIFICATION PROMPT TEMPLATE
# =============================================================================
# This prompt is used by Gemini Flash (gemini-2.5-flash) for fast binary
# classification of the detailed analysis result.
#
# EXACT COPY from layout_verification_app.py line 1516-1523 and 2686-2694
# =============================================================================

CLASSIFICATION_PROMPT_TEMPLATE = """Based on this photonic layout analysis result, provide EXACTLY ONE WORD classification:

Analysis result: {analysis_result}

Instructions:
- If the analysis indicates there are no waveguides, respond with: continuity
- If the analysis indicates any discontinuity, misalignment, step, break, gap, or problem, respond with: discontinuity
- If the analysis indicates the waveguide is continuous, smooth, and properly aligned, respond with: continuity
- Respond with ONLY ONE WORD, no explanation, no punctuation, just: discontinuity OR continuity"""


# =============================================================================
# HELPER FUNCTION
# =============================================================================

def get_classification_prompt(analysis_result: str) -> str:
    """
    Get the classification prompt with the analysis result filled in.
    
    Args:
        analysis_result: The detailed analysis result from Gemini Pro
        
    Returns:
        Complete classification prompt
    """
    return CLASSIFICATION_PROMPT_TEMPLATE.format(analysis_result=analysis_result)


# =============================================================================
# PROMPT VERIFICATION
# =============================================================================
# Version tracking to ensure prompts match original implementation

PROMPT_VERSION = "1.0.0"
ORIGINAL_SOURCE = "layout_verification_app.py"
VERIFICATION_DATE = "2025-10-07"

# Character counts for verification (to detect accidental modifications)
DISCONTINUITY_PROMPT_LENGTH = len(DISCONTINUITY_ANALYSIS_PROMPT)
CLASSIFICATION_PROMPT_LENGTH = len(CLASSIFICATION_PROMPT_TEMPLATE)

# If you modify prompts, update this verification info:
# 1. Increment PROMPT_VERSION
# 2. Update VERIFICATION_DATE
# 3. Document changes in comments above
# 4. Test thoroughly with real photonic layouts!

