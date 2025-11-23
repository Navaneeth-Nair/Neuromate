# tts.py
import pyttsx3
import keyboard
from database import MoodEntry
from typing import Optional, Dict, Any
import threading
import time
import sys
import os

# Try to import Windows COM for direct SAPI access (more reliable than pyttsx3)
try:
    import win32com.client
    WINDOWS_COM_AVAILABLE = True
except ImportError:
    WINDOWS_COM_AVAILABLE = False


class TTSEngine:
    """Text-to-speech engine with tone presets"""
    
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.voices = self.engine.getProperty("voices")
            # Ensure volume is set
            self.engine.setProperty("volume", 1.0)
            # Ensure rate is reasonable
            self.engine.setProperty("rate", 250)
            self._setup_default_voice()
            print(f"[TTS] Engine initialized with {len(self.voices)} voice(s)")
            # Connect to engine events to track speech completion
            self._is_speaking = False
            # Store default voice ID for reuse
            self.default_voice_id = self.engine.getProperty("voice")
            # Lock to ensure only one speech at a time
            self._speech_lock = threading.Lock()
        except Exception as e:
            print(f"[TTS] Error initializing engine: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    
    def _setup_default_voice(self):
        """Setup default voice"""
        if len(self.voices) > 1:
            self.engine.setProperty("voice", self.voices[1].id)
        else:
            self.engine.setProperty("voice", self.voices[0].id)
    
    def set_tone(self, tone: str = "neutral"):
        """
        Set TTS tone based on mood/context
        
        Args:
            tone: "calm", "cheerful", "focused", or "neutral"
        """
        self._apply_tone_to_engine(self.engine, tone)
    
    def _apply_tone_to_engine(self, engine, tone: str = "neutral"):
        """
        Apply tone settings to an engine instance
        
        Args:
            engine: pyttsx3 engine instance
            tone: "calm", "cheerful", "focused", or "neutral"
        """
        if tone == "calm":
            # Slower, softer for low mood or stress
            engine.setProperty("rate", 200)
            engine.setProperty("volume", 0.8)
        elif tone == "cheerful":
            # Faster, brighter for good mood
            engine.setProperty("rate", 280)
            engine.setProperty("volume", 1.0)
        elif tone == "focused":
            # Clear, moderate for work/planning
            engine.setProperty("rate", 250)
            engine.setProperty("volume", 0.9)
        else:  # neutral
            engine.setProperty("rate", 250)
            engine.setProperty("volume", 1.0)
    
    def get_tone_from_mood(self, mood_score: int) -> str:
        """Determine tone based on mood score"""
        if mood_score >= 7:
            return "cheerful"
        elif mood_score >= 5:
            return "neutral"
        else:
            return "calm"
    
    def get_enhanced_tone_config(self, mood_score: Optional[int] = None, 
                                 context: str = "general") -> Dict[str, Any]:
        """
        Get enhanced tone configuration using motivation engine
        
        Args:
            mood_score: Current mood score (1-10)
            context: Context of interaction
            
        Returns:
            Dictionary with tone configuration (rate, volume, phrasing_style, etc.)
        """
        try:
            from .motivation_engine import get_motivation_engine
            engine = get_motivation_engine()
            tone_name, tone_config = engine.get_enhanced_tone(mood_score, context)
            return tone_config
        except Exception as e:
            # Fallback to basic tone
            if mood_score is None:
                mood_score = 5
            if mood_score >= 7:
                return {"rate": 280, "volume": 1.0}
            elif mood_score >= 5:
                return {"rate": 250, "volume": 1.0}
            else:
                return {"rate": 200, "volume": 0.8}
    
    def speak(self, text: str = None, tone: str = None, block_keys: bool = True):
        """
        Speak text with optional tone
        
        Args:
            text: Text to speak (if None, reads from response.txt)
            tone: Tone preset ("calm", "cheerful", "focused", "neutral")
            block_keys: Whether to block ENTER/ESC keys during speech (default: True)
                        Set to False for text input mode
        """
        # CRITICAL: Stop any previous speech and reset engine state
        # This ensures the engine is ready for new speech, especially for consecutive calls
        # pyttsx3 on Windows can get stuck if not properly reset between calls
        import time
        try:
            # Stop any ongoing speech multiple times to ensure it's stopped
            for _ in range(3):
                try:
                    self.engine.stop()
                except:
                    pass
                time.sleep(0.05)
            
            # Additional delay to ensure engine state is fully reset
            time.sleep(0.15)
            
            # Verify and reset engine properties to ensure it's ready
            try:
                self.engine.setProperty("volume", 1.0)
                self.engine.setProperty("rate", 250)
            except:
                pass
        except:
            pass
        
        # Only block keys if requested (default True for voice mode, False for text mode)
        if block_keys:
            try:
                keyboard.block_key('enter')
                keyboard.block_key('esc')
            except:
                pass  # Keyboard blocking might fail, continue anyway
        
        if text is None:
            try:
                with open("data/response.txt", 'r', encoding='utf-8') as f:
                    text = f.read().strip()
            except FileNotFoundError:
                print("No response text found.")
                if block_keys:
                    try:
                        keyboard.unblock_key('enter')
                        keyboard.unblock_key('esc')
                    except:
                        pass
                return
        
        if not text:
            if block_keys:
                try:
                    keyboard.unblock_key('enter')
                    keyboard.unblock_key('esc')
                except:
                    pass
            return
        
        # Determine tone if not specified
        if tone is None:
            try:
                mood_entry = MoodEntry.get_today()
                if mood_entry:
                    tone = self.get_tone_from_mood(mood_entry.mood_score)
                else:
                    tone = "neutral"
            except:
                tone = "neutral"
        
        # Set tone
        self.set_tone(tone)
        
        # Clean text: remove markdown formatting and special characters
        import re
        # Remove markdown bold/italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *italic* -> italic
        text = re.sub(r'__([^_]+)__', r'\1', text)  # __bold__ -> bold
        text = re.sub(r'_([^_]+)_', r'\1', text)  # _italic_ -> italic
        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove markdown list markers
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        # Replace multiple newlines with single space
        text = re.sub(r'\n+', ' ', text)
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        
        if not text:
            print("[TTS] Warning: Text is empty after cleaning")
            return
        
        # Speak - split long text into sentences to avoid truncation
        try:
            print(f"[TTS] Preparing to speak ({len(text)} characters after cleaning)...")
            
            # Split text into sentences for better TTS handling
            # This prevents truncation issues with very long responses
            
            # Split by sentence endings (period, exclamation, question mark)
            # This regex finds sentence boundaries more reliably
            sentence_pattern = r'([.!?]+)\s*'
            parts = re.split(sentence_pattern, text)
            
            # Recombine sentences with their punctuation
            chunks = []
            i = 0
            while i < len(parts):
                if i + 1 < len(parts) and parts[i + 1].strip():
                    # Sentence + punctuation
                    chunk = parts[i].strip() + parts[i + 1].strip()
                    if chunk:
                        chunks.append(chunk)
                    i += 2
                else:
                    if parts[i].strip():
                        chunks.append(parts[i].strip())
                    i += 1
            
            # Filter out empty chunks and ensure each chunk ends with punctuation
            filtered_chunks = []
            for chunk in chunks:
                chunk = chunk.strip()
                if chunk:
                    # Ensure chunk ends with punctuation for natural speech
                    if not re.search(r'[.!?]$', chunk):
                        chunk += '.'
                    filtered_chunks.append(chunk)
            chunks = filtered_chunks
            
            # If no sentence breaks found, try splitting by newlines
            if len(chunks) == 0 or (len(chunks) == 1 and len(text) > 500):
                # Split by double newlines (paragraphs)
                paragraphs = text.split('\n\n')
                if len(paragraphs) > 1:
                    chunks = [p.strip() for p in paragraphs if p.strip()]
                else:
                    # Split by single newlines
                    lines = text.split('\n')
                    if len(lines) > 1:
                        chunks = [line.strip() for line in lines if line.strip()]
                    else:
                        # Last resort: split by commas if very long
                        if len(text) > 800:
                            comma_splits = text.split(', ')
                            if len(comma_splits) > 3:
                                # Group into chunks of ~500 chars
                                chunks = []
                                current_chunk = ""
                                for split in comma_splits:
                                    if len(current_chunk) + len(split) < 500:
                                        current_chunk += split + ", "
                                    else:
                                        if current_chunk:
                                            chunks.append(current_chunk.rstrip(", "))
                                        current_chunk = split + ", "
                                if current_chunk:
                                    chunks.append(current_chunk.rstrip(", "))
                            else:
                                chunks = [text]
                        else:
                            chunks = [text]
            
            # CRITICAL: pyttsx3 chunking with multiple engines doesn't work reliably on Windows
            # Only the first chunk is heard when using multiple engine instances
            # Best solution: Increase threshold so most responses are spoken without chunking
            # Most AI responses are 400-800 chars, which can be handled in one go
            # Windows COM SAPI can handle longer text reliably, so we use 1500 chars as threshold
            # Only chunk for very long responses (>1500 chars) as a last resort
            if len(text) <= 1500:
                print(f"[TTS] Text length ({len(text)} chars) is within limit, speaking without chunking...")
                try:
                    # CRITICAL FIX: Use threading lock to ensure only one speech at a time
                    # and create a completely fresh engine instance for each call.
                    # pyttsx3 on Windows requires this for reliable consecutive calls.
                    
                    with self._speech_lock:
                        # CRITICAL FIX: Try Windows COM SAPI first (more reliable for consecutive calls)
                        # pyttsx3 has a known bug on Windows where only the first call works
                        if WINDOWS_COM_AVAILABLE and sys.platform == 'win32':
                            print(f"[TTS] Using Windows COM SAPI for reliable consecutive calls...")
                            try:
                                # Create SAPI speaker directly via COM
                                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                                
                                # Set voice if we have a default
                                if hasattr(self, 'default_voice_id') and self.default_voice_id:
                                    try:
                                        voices = speaker.GetVoices()
                                        for i in range(voices.Count):
                                            voice = voices.Item(i)
                                            if self.default_voice_id in voice.Id or self.default_voice_id in str(voice):
                                                speaker.Voice = voice
                                                break
                                    except Exception as voice_error:
                                        print(f"[TTS] Could not set voice: {voice_error}")
                                
                                # Determine tone if not specified
                                if tone is None:
                                    try:
                                        mood_entry = MoodEntry.get_today()
                                        if mood_entry:
                                            tone = self.get_tone_from_mood(mood_entry.mood_score)
                                    except:
                                        tone = "neutral"
                                
                                # Set rate (SAPI uses -10 to 10, where 0 is normal)
                                # pyttsx3 rate 250 ≈ SAPI rate 0
                                rate = 0  # Default (normal speed)
                                if tone == "calm":
                                    rate = -2  # Slower
                                elif tone == "cheerful":
                                    rate = 2   # Faster
                                elif tone == "focused":
                                    rate = 0   # Normal
                                
                                try:
                                    speaker.Rate = rate
                                except:
                                    pass
                                
                                # Set volume (0-100)
                                volume = 100
                                if tone == "calm":
                                    volume = 80
                                elif tone == "focused":
                                    volume = 90
                                
                                try:
                                    speaker.Volume = volume
                                except:
                                    pass
                                
                                # Speak synchronously (0 = synchronous, 1 = asynchronous)
                                print(f"[TTS] Speaking via Windows COM: '{text[:50]}...'")
                                speaker.Speak(text, 0)
                                print(f"[TTS] Speech completed.")
                                
                                # Clean up COM object
                                del speaker
                                
                                # Small delay to ensure audio completes
                                time.sleep(0.2)
                                return
                                
                            except Exception as com_error:
                                print(f"[TTS] Windows COM failed: {com_error}")
                                print(f"[TTS] Falling back to pyttsx3...")
                                import traceback
                                traceback.print_exc()
                                # Fall through to pyttsx3 fallback
                        
                        # FALLBACK: Use pyttsx3 with fresh engine (less reliable on Windows)
                        print(f"[TTS] Using pyttsx3 (may have issues with consecutive calls on Windows)...")
                        
                        # Create a completely new engine instance
                        fresh_engine = None
                        try:
                            fresh_engine = pyttsx3.init()
                            
                            # Set properties
                            fresh_engine.setProperty("volume", 1.0)
                            fresh_engine.setProperty("rate", 250)
                            if hasattr(self, 'default_voice_id'):
                                try:
                                    fresh_engine.setProperty("voice", self.default_voice_id)
                                except:
                                    pass
                            
                            # Apply tone settings
                            if tone:
                                self._apply_tone_to_engine(fresh_engine, tone)
                            else:
                                # Determine tone from mood if not specified
                                try:
                                    mood_entry = MoodEntry.get_today()
                                    if mood_entry:
                                        tone = self.get_tone_from_mood(mood_entry.mood_score)
                                        self._apply_tone_to_engine(fresh_engine, tone)
                                except:
                                    pass
                            
                            # Small delay to ensure engine is ready
                            time.sleep(0.2)
                            
                            # Speak the text
                            print(f"[TTS] Speaking: '{text[:50]}...'")
                            fresh_engine.say(text)
                            fresh_engine.runAndWait()
                            print(f"[TTS] Speech completed.")
                            
                            # Wait for audio to complete
                            time.sleep(0.5)
                            
                        finally:
                            # Always clean up the fresh engine
                            if fresh_engine:
                                try:
                                    fresh_engine.stop()
                                    del fresh_engine
                                except:
                                    pass
                                import gc
                                gc.collect()
                                time.sleep(0.3)
                        
                        return
                    
                except Exception as e:
                    print(f"[TTS] Error speaking full text: {e}")
                    import traceback
                    traceback.print_exc()
                    print(f"[TTS] Will try chunking as fallback...")
                    # Fall through to chunking approach
                except Exception as e:
                    print(f"[TTS] Error speaking full text: {e}")
                    import traceback
                    traceback.print_exc()
                    print(f"[TTS] Will try chunking as fallback...")
                    # Fall through to chunking approach
            else:
                print(f"[TTS] Text length ({len(text)} chars) exceeds 1500 char limit, will chunk to ensure all text is spoken...")
            
            # Ensure we have at least one chunk
            if not chunks:
                chunks = [text]
            
            # Speak each chunk sequentially
            # CRITICAL: For pyttsx3 on Windows, chunking with fresh engines doesn't work reliably
            # Try using the main engine with proper delays instead
            print(f"[TTS] Splitting into {len(chunks)} chunk(s)...")
            
            # Clean all chunks first
            cleaned_chunks = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    # Clean chunk: remove any remaining markdown/special chars
                    clean_chunk = re.sub(r'\*\*([^*]+)\*\*', r'\1', chunk)
                    clean_chunk = re.sub(r'\*([^*]+)\*', r'\1', clean_chunk)
                    clean_chunk = re.sub(r'__([^_]+)__', r'\1', clean_chunk)
                    clean_chunk = re.sub(r'_([^_]+)_', r'\1', clean_chunk)
                    clean_chunk = re.sub(r'\n+', ' ', clean_chunk)
                    clean_chunk = re.sub(r'\s+', ' ', clean_chunk)
                    clean_chunk = clean_chunk.strip()
                    
                    if clean_chunk:
                        cleaned_chunks.append((i+1, clean_chunk))
                        chunk_preview = clean_chunk[:60] + "..." if len(clean_chunk) > 60 else clean_chunk
                        print(f"[TTS] Prepared chunk {i+1}/{len(chunks)}: {chunk_preview}")
            
            if not cleaned_chunks:
                print("[TTS] No valid chunks to speak")
                return
            
            try:
                # Ensure engine properties are set
                self.set_tone(tone)
                
                # Verify engine is still valid
                if not self.engine:
                    print("[TTS] ERROR: Engine is None, reinitializing...")
                    self.engine = pyttsx3.init()
                    self.set_tone(tone)
                
                # Verify volume and rate
                current_volume = self.engine.getProperty("volume")
                current_rate = self.engine.getProperty("rate")
                print(f"[TTS] Engine properties - Volume: {current_volume}, Rate: {current_rate}")
                
                if current_volume == 0:
                    print("[TTS] WARNING: Volume is 0! Setting to 1.0")
                    self.engine.setProperty("volume", 1.0)
                    current_volume = 1.0
                
                # CRITICAL: pyttsx3 on Windows has issues with multiple engine instances
                # Try using the main engine with proper queueing and delays
                print(f"[TTS] Speaking {len(cleaned_chunks)} chunk(s) using main engine...")
                import time
                
                # CRITICAL: Queueing doesn't work reliably - only first chunk is heard
                # Sequential with same engine also has issues
                # Best approach: Create fresh engine for each chunk (we know this works from tests)
                # But we need to ensure each chunk completes before next starts
                main_voice_id = self.engine.getProperty("voice")
                
                for chunk_num, clean_chunk in cleaned_chunks:
                    print(f"[TTS] Speaking chunk {chunk_num}/{len(cleaned_chunks)} ({len(clean_chunk)} chars)...")
                    print(f"[TTS] Chunk text: '{clean_chunk[:80]}...'")
                    
                    try:
                        # CRITICAL: Wait before creating new engine (except for first chunk)
                        # This ensures previous audio output is completely finished
                        if chunk_num > 1:
                            print(f"[TTS] Waiting before chunk {chunk_num}...")
                            time.sleep(0.8)  # Longer delay to ensure previous audio completes
                        
                        # Create fresh engine for each chunk
                        print(f"[TTS] Creating engine for chunk {chunk_num}...")
                        chunk_engine = pyttsx3.init()
                        
                        # Set properties
                        chunk_engine.setProperty("volume", current_volume)
                        chunk_engine.setProperty("rate", current_rate)
                        chunk_engine.setProperty("voice", main_voice_id)
                        
                        # Verify properties
                        verify_vol = chunk_engine.getProperty("volume")
                        verify_rate = chunk_engine.getProperty("rate")
                        print(f"[TTS] Chunk {chunk_num} engine - Volume: {verify_vol}, Rate: {verify_rate}")
                        
                        if verify_vol == 0:
                            print(f"[TTS] WARNING: Volume is 0! Setting to 1.0")
                            chunk_engine.setProperty("volume", 1.0)
                        
                        # Speak chunk
                        print(f"[TTS] Queueing chunk {chunk_num}...")
                        chunk_engine.say(clean_chunk)
                        print(f"[TTS] Running engine for chunk {chunk_num}...")
                        
                        # CRITICAL: runAndWait() should block until speech completes
                        chunk_engine.runAndWait()
                        print(f"[TTS] Chunk {chunk_num} runAndWait() completed.")
                        
                        # Additional wait to ensure audio output is flushed
                        time.sleep(0.3)
                        print(f"[TTS] Chunk {chunk_num} fully completed.")
                        
                        # Clean up engine completely
                        try:
                            chunk_engine.stop()
                        except:
                            pass
                        try:
                            del chunk_engine
                        except:
                            pass
                        # Force garbage collection
                        import gc
                        gc.collect()
                        
                        # Longer pause between chunks to ensure Windows audio system is ready
                        if chunk_num < len(cleaned_chunks):
                            print(f"[TTS] Pausing before next chunk...")
                            time.sleep(0.6)  # Longer pause for Windows audio system
                        
                    except Exception as chunk_error:
                        print(f"[TTS] ERROR speaking chunk {chunk_num}: {chunk_error}")
                        import traceback
                        traceback.print_exc()
                        # Try to continue with next chunk
                        continue
                
                print(f"[TTS] All {len(cleaned_chunks)} chunk(s) completed.")
                
            except Exception as e:
                print(f"[TTS] Error speaking chunks: {e}")
                import traceback
                traceback.print_exc()
            
            print(f"[TTS] Finished speaking all {len(chunks)} chunk(s).")
        except Exception as e:
            print(f"[TTS] Error in TTS engine: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: try to speak the whole text
            try:
                print("[TTS] Attempting fallback: speaking entire text...")
                self.engine.say(text)
                self.engine.runAndWait()
                print("[TTS] Fallback completed.")
            except Exception as e2:
                print(f"[TTS] Fallback also failed: {e2}")
                import traceback
                traceback.print_exc()
        
        # DON'T clear response.txt here - let it persist for potential re-reading
        # The file will be overwritten on the next response anyway
        # Clearing it here can cause issues if TTS needs to re-read it
        
        # CRITICAL: Ensure keys are unblocked after speaking (only if we blocked them)
        # Add a small delay to ensure key state is properly reset
        if block_keys:
            import time
            try:
                keyboard.unblock_key('enter')
                keyboard.unblock_key('esc')
                time.sleep(0.1)  # Small delay to ensure unblock takes effect
            except Exception as unblock_error:
                print(f"[TTS] Warning: Could not unblock keys: {unblock_error}")
                # Try again
                try:
                    keyboard.unblock_key('enter')
                    keyboard.unblock_key('esc')
                except:
                    pass


# Global TTS engine instance
_tts_engine = TTSEngine()


def speak(text: str = None, tone: str = None, block_keys: bool = True):
    """
    Convenience function for speaking
    
    Args:
        text: Text to speak (if None, reads from response.txt)
        tone: Tone preset ("calm", "cheerful", "focused", "neutral")
        block_keys: Whether to block ENTER/ESC keys during speech (default: True)
    """
    _tts_engine.speak(text, tone, block_keys)


if __name__ == "__main__":
    speak()

