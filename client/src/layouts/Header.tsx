import { useState, useRef, useEffect } from 'react';
import { RxDropdownMenu } from 'react-icons/rx';
import { FaEarListen } from 'react-icons/fa6';
import { RiSpeakLine } from 'react-icons/ri';
import { PiDiamondsFourFill } from 'react-icons/pi';
import { IoIosNotificationsOutline } from 'react-icons/io';
import { IoSearch } from 'react-icons/io5';
import { useNavigate } from 'react-router-dom';
import ProfileImg from '../assets/profileimg.jfif';
import api from '../utils/api';
import { sideBarArrayList } from '../utils/sidebar';

export const Header = () => {
  const [state, setState] = useState({
    menu: false,
    listen: false,
    voice: false,
    activeIndex: 0,
    audioBlob: null as Blob | null,
    isRecording: false,
    store: { name: '', email: '' },
    error: null as string | null,
  });

  const nav = useNavigate();
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  useEffect(() => {
    const fetchStoreName = async () => {
      try {
        const response = await api.get(`/settings/store/get/`);
        setState((prevState) => ({ ...prevState, store: response.data }));
      } catch (error) {
        console.error('Error fetching store name:', error);
      }
    };

    fetchStoreName();
  }, []);

  const startRecording = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            setState((prevState) => ({ ...prevState, audioBlob: event.data }));
          }
        };

        mediaRecorder.start(900);
        setState((prevState) => ({ ...prevState, isRecording: true }));
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
      setState((prevState) => ({ ...prevState, isRecording: false }));
    }
  };

  useEffect(() => {
    if (state.listen) {
      startRecording();
    } else {
      stopRecording();
    }
  }, [state.listen]);

  const handleUpload = async () => {
    if (state.audioBlob) {
      const formData = new FormData();
      formData.append('file', new File([state.audioBlob], 'audio.webm', { type: 'audio/webm' }));

      try {
        await api.post(`/query/upload/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setState((prevState) => ({ ...prevState, error: null }));
      } catch (error) {
        console.error('Error uploading audio:', error);
        setState((prevState) => ({ ...prevState, error: 'Failed to upload audio. Please try again.' }));
      }
    } else {
      setState((prevState) => ({ ...prevState, error: 'No audio data available for upload.' }));
    }
  };

  return (
    <div className='Header_Container'>
      {state.error && <div className="error-message">{state.error}</div>}
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
            <input type="text" placeholder="Search anything..." />
            <p onClick={() => setState((prevState) => ({ ...prevState, voice: !state.voice }))}>
              <RiSpeakLine />
            </p>
          </>
        )}
      </section>
      <section className="RightHand_Container">
        <p className="Exclusive_Store">{state.store.name || "Store Name"}</p>
        <p><IoIosNotificationsOutline /></p>
        <div className="Image_Container">
          <img src={ProfileImg} alt="profile" />
        </div>
      </section>
      <p onClick={() => setState((prevState) => ({ ...prevState, menu: !state.menu }))} className="Mobile_Menu"><RxDropdownMenu /></p>
      {state.menu && (
        <article className="Mobile_Menu_Nav">
          {sideBarArrayList.map((obj, index) => (
            <span
              key={index}
              onClick={() => {
                setState((prevState) => ({ ...prevState, activeIndex: index, menu: false }));
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
            setState((prevState) => ({ ...prevState, voice: false, listen: true }));
          }}
          className="Search_By_Voice"
        >
          Search By Voice
        </span>
      )}
      {state.listen && (
        <span
          onClick={() => {
            setState((prevState) => ({ ...prevState, listen: false }));
            handleUpload();
          }}
          className="Search_By_Voice Stop_Voice"
        >
          Stop recording
        </span>
      )}
    </div>
  );
};
