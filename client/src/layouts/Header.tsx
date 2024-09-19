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
  const [state, setState] = useState({
    menu: false,
    listen: false,
    voice: false,
    pop: false,
    popup: false,
    activeIndex: 0,
    errorMessage: '',
    firstname: 'Hassan',
    lastname: 'ademidun',
    emailadress: 'hassan@gmail.com',
    phonenumber: '081284658474',
    loading: false,
    audioBlob: null as Blob | null,
    isRecording: false,
    store: { name: "", email: "" },
    searchQuery: '',
    searchResults: [] as any[],
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
          } else {
            console.error("No audio chunks available.");
          }
        };

        mediaRecorder.start();
        setState(prevState => ({ ...prevState, isRecording: true }));
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

        const parsed_response = JSON.parse(response.data.results)
        const type = response.data.type
        console.log(parsed_response)
        if (response.status === 200) {
          if (parsed_response.type === "UPDATE") {
            
           
            console.log(parsed_response)
          } else if (type === "INSERT" && parsed_response.incomplete_fields) {
            
            console.log(parsed_response)
          } else if (type === "SELECT") {
            nav('/query', { state: { data: parsed_response.results, header: 'Query Results' } });
          } else if (type === "DELETE") {
            // Handle DELETE logic here
            console.log(parsed_response)
          }
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

      {state.popup && (
        <div className="Popup_Container">
          {/* Content for the popup box goes here */}
          <p>Popup Content</p>
        </div>
      )}

      <section className="RightHand_Container">
        <p className="Exclusive_Store">{state.store.name || "Store Name"}</p>
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
          onClick={() => setState(prevState => ({ ...prevState, voice: false, listen: true }))}
          className="Search_By_Voice"
        >
          Search By Voice
        </span>
      )}

      {state.listen && (
        <span
          onClick={() => setState(prevState => ({ ...prevState, listen: false }))}
          className="Search_By_Voice Stop_Voice"
        >
          Stop recording
        </span>
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

      <article className='Main_action_pop'>
        <h1>Are you Sure you want to UPDATE? </h1>
        <form>
          <input
           type="text"
           value={state.firstname}
           onChange={(e)=> setState(prevState => ({ ...prevState, firstname:e.target.value  }))}
          placeholder='First Name'/>
          <input
           value={state.lastname}
           onChange={(e)=> setState(prevState => ({ ...prevState, lastname:e.target.value  }))}
           type="text" 
           placeholder='Last Name'/>
          <input
           value={state.emailadress}
           onChange={(e)=> setState(prevState => ({ ...prevState, emailadress:e.target.value  }))}
           type="email" 
           placeholder='email address'/>
          <input
           type="text" 
           value={state.phonenumber}
           onChange={(e)=> setState(prevState => ({ ...prevState, phonenumber:e.target.value  }))}
           placeholder='phone number'/>
          <button>Update</button>
        </form>
      </article>

    </div>
  );
};
