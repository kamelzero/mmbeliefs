## LMMS Usage

# Point to Your Dataset

In `lmms-eval-files/mmbeliefs_mcq/_default_template_mmbeliefs_yaml`

swap out the dataset name with your HF dataset name.

# Ensure Gemini 2.5 Support

The Gemini 2.5 models don't run properly with the generation_config passed in.

```
diff --git a/lmms_eval/models/gemini_api.py b/lmms_eval/models/gemini_api.py
index 1d5a770..4f2f75e 100644
--- a/lmms_eval/models/gemini_api.py
+++ b/lmms_eval/models/gemini_api.py
@@ -191,7 +191,7 @@ class GeminiAPI(lmms):
                 try:
                     content = self.model.generate_content(
                         message,
-                        generation_config=config,
+                        #generation_config=config,
                         safety_settings={
                             HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                             HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
```
