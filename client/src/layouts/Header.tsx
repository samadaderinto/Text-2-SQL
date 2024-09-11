import { useEffect, useRef, useState } from 'react';
import { FaEarListen } from "react-icons/fa6";
import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch } from "react-icons/io5";
import { PiDiamondsFourFill } from "react-icons/pi";
import { RiSpeakLine } from "react-icons/ri";
import { RxDropdownMenu } from "react-icons/rx";
import { useNavigate } from 'react-router-dom';
import ProfileImg from "../assets/profileimg.jfif";
import ClipLoader from 'react-spinners/ClipLoader';
import api from '../utils/api';
import { sideBarArrayList } from '../utils/sidebar';

export const Header = () => {
  const [state, setState] = useState<{
    menu: boolean;
    listen: boolean;
    voice: boolean;
    activeIndex: number;
    errorMessage: string;
    loading: boolean;
    audioBlob: Blob | null;
    isRecording: boolean;
    store: { name: string; email: string };
    searchQuery: string;  
    searchResults: any[]; 
  }>({
    menu: false,
    listen: false,
    voice: false,
    activeIndex: 0,
    errorMessage: '',
    loading: false,
    audioBlob: null,
    isRecording: false,
    store: { name: "", email: "" },
    searchQuery: '',
    searchResults: []  // Initialize searchResults state
  });

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
      try {
        const response = await api.get(`query/search/`, { params: { query: state.searchQuery } });
        setState(prevState => ({ ...prevState, searchResults: response.data }));
      } catch (error) {
        console.error('Error performing search:', error);
      }
    } else {
      setState(prevState => ({ ...prevState, searchResults: [] }));
    }
  };

  useEffect(() => {

    performSearch();
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
          console.log(response.data.results)
          // if (response.data.type == "UPDATE") {
          //   console.log(response.data)

          // } else if (response.data.type == "INSERT") {
          //   console.log(response.data)
        
            nav('/query', { state: { data: response.data.results, header: 'Query Results' } });
        }
      } catch (error: any) {
        if (error.response && error.response.status === 500) {
          setState(prevState => ({ ...prevState, errorMessage: 'Unable to process your audio request. Please try again.' }));
        } else {
          setState(prevState => ({ ...prevState, errorMessage: 'Unable to find what you\'re looking for. Please try again.' }));
        }
        console.error('Error uploading audio:', error);
      } finally {
        setState(prevState => ({ ...prevState, loading: false }));
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
              onChange={(e) => setState(prevState => ({ ...prevState, searchQuery: e.target.value }))}
              onKeyDown={(e) => e.key === 'Enter' && performSearch()}
            />
            <p onClick={() => setState(prevState => ({ ...prevState, voice: !state.voice }))}><RiSpeakLine /></p>
          </>
        )}
      </section>
      <section className="RightHand_Container">
        <p className="Exclusive_Store">{state.store.name ? state.store.name : "Store Name"}</p>
        <p><IoIosNotificationsOutline /></p>
        <div className="Image_Container">
          <img src={ProfileImg} alt="profile" />
        </div>
      </section>
      <p onClick={() => setState(prevState => ({ ...prevState, menu: !state.menu }))} className="Mobile_Menu"><RxDropdownMenu /></p>
      {state.menu && (
        <article className="Mobile_Menu_Nav">
          {sideBarArrayList.map((obj, index) => (
            <span
              key={index}
              onClick={() => {
                setState(prevState => ({ ...prevState, activeIndex: index, menu: false }));
                nav(`/${obj.itemName}`);
              }}
              className={state.activeIndex === index ? 'Active_List' : ''}
            >
              <p className="List_icon">{obj.icon}</p>
              <p>{obj.itemName}</p>
            </span>
          ))}
        </article>
      )}
      {state.voice && (
        <span
          onClick={() => {
            setState(prevState => ({ ...prevState, voice: false, listen: true }));
          }}
          className="Search_By_Voice"
        >
          Search By Voice
        </span>
      )}
      {state.listen && (
        <span
          onClick={() => {
            setState(prevState => ({ ...prevState, listen: false }));
          }}
          className="Search_By_Voice Stop_Voice">
          Stop recording
        </span>
      )}

      {state.loading && (
        <div className="loading-spinner">
          <ClipLoader color={"#123abc"} loading={state.loading} size={50} />
        </div>
      )}

      {state.errorMessage && <p className="error-message">{state.errorMessage}</p>}
      
     
      {state.searchQuery && (
        <div className="search-results">
          {state.searchResults.length > 0 ? (
            state.searchResults.map((result, index) => (
              <div key={index} className="search-result-item">
   
                <p>{result.name}</p> 
              </div>
            ))
          ) : (
            <p>No results found</p>
          )}
        </div>
      )}
    </div>
  );
};
