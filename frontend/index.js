/**
 * @license
 * Copyright 2020 Google LLC. All Rights Reserved.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * =============================================================================
 */

import * as tfwebgpu from '@tensorflow/tfjs-backend-webgpu';
import * as tf from '@tensorflow/tfjs-core';
import * as handpose from '@tensorflow-models/handpose';
import * as tfjsWasm from '@tensorflow/tfjs-backend-wasm';
// TODO(annxingyuan): read version from tfjsWasm directly once
// https://github.com/tensorflow/tfjs/pull/2819 is merged.
import {version} from '@tensorflow/tfjs-backend-wasm/dist/version';


var socket = new WebSocket("ws://localhost:8765");



tfjsWasm.setWasmPath(
    `https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-wasm@${
        version}/dist/tfjs-backend-wasm.wasm`);
function isMobile() {
  const isAndroid = /Android/i.test(navigator.userAgent);
  const isiOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
  return isAndroid || isiOS;
}

let videoWidth, videoHeight, scatterGLHasInitialized = false, scatterGL,
  fingerLookupIndices = {
    thumb: [0, 1, 2, 3, 4],
    indexFinger: [0, 5, 6, 7, 8],
    middleFinger: [0, 9, 10, 11, 12],
    ringFinger: [0, 13, 14, 15, 16],
    pinky: [0, 17, 18, 19, 20]
  }; // for rendering each finger as a polyline

const VIDEO_WIDTH = 640;
const VIDEO_HEIGHT = 500;
const mobile = isMobile();
// Don't render the point cloud on mobile in order to maximize performance and
// to avoid crowding limited screen space.
const renderPointcloud = mobile === false;

var collecting = false;

const state = {
    state: 'Ожидание',
    start_collect: function () {
        console.log("start_collect");
        collecting = true;
        socket.send("start_collect");
    },
    end_collect: function () {
        console.log("end_collect");
        collecting = false;
        socket.send("end_collect");
    },
    save_collected: function () {
        console.log("save_collected");
        socket.send("save_collected" + " " + state.dataset_filename);
        // update("Saved");
    },
    dataset_filename: 'dataset',
    fit: function () {
        console.log("fit");
        socket.send("fit");
    },
    start_predict: function () {
        console.log("start_predict");
        socket.send("start_predict");
    },
    end_predict: function () {
        console.log("end_predict");
        socket.send("end_predict");
    },
    save_model: function () {
        console.log("save_model");
        socket.send("save_model");
    },
    backend: 'webgl',
};

if (renderPointcloud) {
  state.renderPointcloud = true;
}
  

function setupDatGui() {
    const gui = new dat.GUI();

    // gui.add(state, 'state')
    
    var f_data_collect = gui.addFolder('Сбор данных');
    var f_fit = gui.addFolder('Обучение модели');
    var f_predict = gui.addFolder('Анализ данных');
    var f_settings = gui.addFolder('Настройки');

    f_data_collect.add(state, 'start_collect');
    f_data_collect.add(state, 'end_collect');
    f_data_collect.add(state, 'save_collected');
    f_data_collect.add(state, 'dataset_filename');
    f_data_collect.open();

    f_fit.add(state, 'fit');
    // f_fit.add(state, 'dataset_filename');

    f_predict.add(state, 'start_predict');
    f_predict.add(state, 'end_predict');
    f_predict.add(state, 'save_model');


    
    f_settings.add(state, 'backend', ['wasm', 'webgl', 'cpu', 'webgpu'])
        .onChange(async backend => {
            await tf.setBackend(backend);
        });

    if (renderPointcloud) {
        f_settings.add(state, 'renderPointcloud').onChange(render => {
        document.querySelector('#scatter-gl-container').style.display =
            render ? 'inline-block' : 'none';
        });
    }
}
function drawPoint(ctx, y, x, r) {
  ctx.beginPath();
  ctx.arc(x, y, r, 0, 2 * Math.PI);
  ctx.fill();
}

function drawKeypoints(ctx, keypoints) {
  const keypointsArray = keypoints;

  for (let i = 0; i < keypointsArray.length; i++) {
    const y = keypointsArray[i][0];
    const x = keypointsArray[i][1];
    // console.log("Keypoints: ", keypointsArray)
    drawPoint(ctx, x - 2, y - 2, 3);
  }

  const fingers = Object.keys(fingerLookupIndices);
  for (let i = 0; i < fingers.length; i++) {
    const finger = fingers[i];
    const points = fingerLookupIndices[finger].map(idx => keypoints[idx]);
    drawPath(ctx, points, false);
  }
}

function drawPath(ctx, points, closePath) {
  const region = new Path2D();
  region.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) {
    const point = points[i];
    region.lineTo(point[0], point[1]);
  }

  if (closePath) {
    region.closePath();
  }
  ctx.stroke(region);
}

let model;

async function setupCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    throw new Error(
      'Browser API navigator.mediaDevices.getUserMedia not available');
  }

  const video = document.getElementById('video');
  const stream = await navigator.mediaDevices.getUserMedia({
    'audio': false,
    'video': {
      facingMode: 'user',
      // Only setting the video to a specified size in order to accommodate a
      // point cloud, so on mobile devices accept the default size.
      width: mobile ? undefined : VIDEO_WIDTH,
      height: mobile ? undefined : VIDEO_HEIGHT
    },
  });
  video.srcObject = stream;

  return new Promise((resolve) => {
    video.onloadedmetadata = () => {
      resolve(video);
    };
  });
}

async function loadVideo() {
  const video = await setupCamera();
  video.play();
  return video;
}

const main = async () => {
  await tf.setBackend(state.backend);
  model = await handpose.load();
  let video;

  try {
    video = await loadVideo();
  } catch (e) {
    let info = document.getElementById('info');
    info.textContent = e.message;
    info.style.display = 'block';
    throw e;
  }

  

  landmarksRealTime(video);
}

const landmarksRealTime = async (video) => {
  setupDatGui();

  const stats = new Stats();
  stats.showPanel(0);
  document.body.appendChild(stats.dom);

  videoWidth = video.videoWidth;
  videoHeight = video.videoHeight;

  const canvas = document.getElementById('output');

  canvas.width = videoWidth;
  canvas.height = videoHeight;

  const ctx = canvas.getContext('2d');

  video.width = videoWidth;
  video.height = videoHeight;

  ctx.clearRect(0, 0, videoWidth, videoHeight);
  ctx.strokeStyle = "red";
  ctx.fillStyle = "red";

  ctx.translate(canvas.width, 0);
  ctx.scale(-1, 1);

  // These anchor points allow the hand pointcloud to resize according to its
  // position in the input.
  const ANCHOR_POINTS = [[0, 0, 0], [0, -VIDEO_HEIGHT, 0],
  [-VIDEO_WIDTH, 0, 0], [-VIDEO_WIDTH, -VIDEO_HEIGHT, 0]];

  var timer_prev = -1;
  var timer_cnt = 0;
  var time_counter = 0;
  var start_time = Date.now();

  async function frameLandmarks() {
    stats.begin();
    if (collecting){
      var current_time = Date.now();
      timer_cnt  = Math.floor((current_time - start_time) / 100);
      console.log(timer_cnt, timer_prev);
      
      if (timer_cnt > timer_prev){
        document.getElementById("progressBar").value = timer_cnt;
        timer_prev = timer_cnt;
      }
      if (timer_cnt >= 20){
        timer_prev = -1;
        timer_cnt = 0;
        start_time = Date.now();
        time_counter += 2;
        console.log("+ 1 sec");
        document.getElementById("seconds-count").innerText = time_counter + " sec.";
      }
    }
    
    ctx.drawImage(video, 0, 0, videoWidth, videoHeight, 0, 0, canvas.width, canvas.height);
    if (collecting){
      const predictions = await model.estimateHands(video);
      if (predictions.length > 0) {
        const result = predictions[0].landmarks;
        console.log("predictions: ", predictions);
        console.log("result: ", result);
        drawKeypoints(ctx, result, predictions[0].annotations);
        socket.send("dk" + result);

        if (renderPointcloud === true && scatterGL != null) {
          const pointsData = result.map(point => {
            return [-point[0], -point[1], -point[2]];
          });
          // console.log(pointsData)
          const dataset = new ScatterGL.Dataset([...pointsData, ...ANCHOR_POINTS]);

          if (!scatterGLHasInitialized) {
            scatterGL.render(dataset);

            const fingers = Object.keys(fingerLookupIndices);

            scatterGL.setSequences(fingers.map(finger => ({ indices: fingerLookupIndices[finger] })));
            scatterGL.setPointColorer((index) => {
              if (index < pointsData.length) {
                return 'steelblue';
              }
              return 'white'; // Hide.
            });
          } else {
            scatterGL.updateDataset(dataset);
          }
          scatterGLHasInitialized = true;
        }
      }
    }
    stats.end();
    requestAnimationFrame(frameLandmarks);
  };

  frameLandmarks();

  if (renderPointcloud) {
    document.querySelector('#scatter-gl-container').style =
      `width: ${VIDEO_WIDTH}px; height: ${VIDEO_HEIGHT}px;`;

    scatterGL = new ScatterGL(
      document.querySelector('#scatter-gl-container'),
      { 'rotateOnStart': false, 'selectEnabled': false });
  }
};

navigator.getUserMedia = navigator.getUserMedia ||
  navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

main();
