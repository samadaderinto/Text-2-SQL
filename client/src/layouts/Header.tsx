import { useEffect, useRef, useState } from 'react';
import { FaEarListen } from "react-icons/fa6";
import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch } from "react-icons/io5";
import { PiDiamondsFourFill } from "react-icons/pi";
import { RiSpeakLine } from "react-icons/ri";
import { RxDropdownMenu } from "react-icons/rx";
import { useNavigate } from 'react-router-dom';
import ProfileImg from "../assets/profileimg.jfif";
import { Oval } from 'react-loader-spinner';
import api from '../utils/api';
import { sideBarArrayList } from '../utils/sidebar';

export const Header = () => {
  const [state, setState] = useState<{
    menu: boolean;
    listen: boolean;
    pop: boolean;
    loading: boolean;
    voice: boolean;
    activeIndex: number;
    errorMessage: string;
    audioBlob: Blob | null;
    isRecording: boolean;
    store: { name: string; email: string };
    searchQuery: string;  
    searchResults: any[]; 
    showPopup: boolean;
    apiResult: string;
  }>({
    menu: false,
    listen: false,
    voice: false,
    pop: false,
    activeIndex: 0,
    errorMessage: '',
    loading: false,
    audioBlob: null,
    isRecording: false,
    store: { name: "", email: "" },
    searchQuery: '',
    searchResults: [],
    showPopup: false,  // New state for popup visibility
    apiResult: '',  // New state for API result content
  });

  const HandlePop = ()=> {
    if(state.searchQuery !== '') {
      setState(prevState => ({ ...prevState, pop: true }))
    } else {
      setState(prevState => ({ ...prevState, pop: false }))
    }
  }

  useEffect(() => {
    HandlePop();
  }, [state.searchQuery]);
  

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const nav = useNavigate();

  useEffect(() => {
    const fetchStoreName = async () => {
      try {
        const response = await api.get(`/settings/store/get/`);
        setState(prevState => ({ ...prevState, store: response.data }));
      } catch (error) {
        console.error('Error fetching store name:', error);
      }
    };

    fetchStoreName();
  }, []);

  const performSearch = async () => {
    if (state.searchQuery.trim()) {
      setState(prevState => ({ ...prevState, loading: true })); // Start loading
      try {
        const response = await api.get(`query/search/`, { params: { query: state.searchQuery } });
        setState(prevState => ({
          ...prevState,
          searchResults: response.data,
          loading: false // Stop loading when search completes
        }));
      } catch (error) {
        console.error('Error performing search:', error);
        setState(prevState => ({ ...prevState, searchResults: [], loading: false })); // Stop loading on error
      }
    } else {
      setState(prevState => ({ ...prevState, searchResults: [], loading: false }));
    }
  };

  useEffect(() => {
    if (state.searchQuery) {
      performSearch();
    }
  }, [state.searchQuery]);

  const startRecording = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (mediaRecorderRef.current) {
          mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        mediaRecorderRef.current = mediaRecorder;

        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          if (audioChunksRef.current.length > 0) {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            setState(prevState => ({ ...prevState, audioBlob }));
            console.log("Recording complete and audio blob created.");
          } else {
            console.error("No audio chunks available.");
          }
        };

        mediaRecorder.start();
        setState(prevState => ({ ...prevState, isRecording: true }));
        console.log("Recording started");
      } catch (error) {
        console.error('Error accessing microphone:', error);
      }
    } else {
      console.error('getUserMedia not supported on this browser.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setState(prevState => ({ ...prevState, isRecording: false }));
      console.log("Recording stopped");
    }
  };

  useEffect(() => {
    if (state.listen) {
      startRecording();
    } else {
      stopRecording();
    }
  }, [state.listen]);

  useEffect(() => {
    if (state.audioBlob) {
      handleUpload();
    }
  }, [state.audioBlob]);

  const handleUpload = async () => {
    if (state.audioBlob) {
      const formData = new FormData();
      formData.append('file', new File([state.audioBlob], 'audio.webm', { type: 'audio/webm' }));

      setState(prevState => ({ ...prevState, loading: true }));
      try {
        const response = await api.post(`/query/upload/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.status === 200) {
          console.log(response.data.results);
          setState(prevState => ({
            ...prevState,
            apiResult: response.data.results,  // Store API result
            showPopup: true,  // Show popup after getting result
            loading: false,
          }));
        }
      } catch (error: any) {
        if (error.response && error.response.status === 500) {
          setState(prevState => ({
            ...prevState,
            errorMessage: 'Unable to process your audio request. Please try again.',
            showPopup: true,  // Show popup with error message
            loading: false,
          }));
        } else {
          setState(prevState => ({
            ...prevState,
            errorMessage: 'Unable to find what you\'re looking for. Please try again.',
            showPopup: true,  // Show popup with error message
            loading: false,
          }));
        }
        console.error('Error uploading audio:', error);
      }
    } else {
      setState(prevState => ({ ...prevState, errorMessage: 'No audio data available for upload.' }));
      console.error('No audio data available for upload.');
    }
  };

  return (
    <div className='Header_Container'>
      <span><PiDiamondsFourFill /> EchoCart</span>
      <section className="Search_Container">
        {state.listen ? (
          <>
            <span>Listening...</span>
            <p><FaEarListen /></p>
          </>
        ) : (
          <>
            <p className="Header_Search_Icon"><IoSearch /></p>
            <input 
              type="text" 
              placeholder="Search anything..." 
              value={state.searchQuery} 
              onChange={(e) =>{ setState(prevState => ({ ...prevState, searchQuery: e.target.value })) }}
              onKeyDown={(e) => e.key === 'Enter' && performSearch()}
            />
            <p onClick={() => setState(prevState => ({ ...prevState, voice: !state.voice }))}><RiSpeakLine /></p>
          </>
        )}
      </section>
      {state.pop && (
        <ul className='Pop_Search_Container'>
          <li>Product</li>
          <li>Product</li>
          <li>Product</li>
          <li>Product</li>
          {state.loading && (
            <div className="loading-spinner">
              <Oval
                height={50}
                width={50}
                color="#4fa94d"
                visible={true}
                ariaLabel="oval-loading"
                secondaryColor="#4fa94d"
                strokeWidth={2}
                strokeWidthSecondary={2}
              />
            </div>
          )}
        </ul>
      )}
      
      <section className="RightHand_Container">
        <p className="Exclusive_Store">{state.store.name ? state.store.name : "Store Name"}</p>
        <p><IoIosNotificationsOutline /></p>
        <div className="Image_Container">
          <img src={ProfileImg} alt="profile" />
        </div>
      </section>
      {state.showPopup && (
        <div>
          <div>
            <p>{state.apiResult || state.errorMessage}</p>
            <button onClick={() => setState(prevState => ({ ...prevState, showPopup: false }))}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
