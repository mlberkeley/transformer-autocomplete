

##################################################
INPUT CODE:
##################################################

/* Copyright 2015 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#ifndef TENSORFLOW_CORE_COMMON_RUNTIME_DIRECT_SESSION_H_
#define TENSORFLOW_CORE_COMMON_RUNTIME_DIRECT_SESSION_H_

#include <atomic>
#include <memory>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "tensorflow/core/common_runtime/costmodel_manager.h"
#include "tensorflow/core/common_runtime/debugger_state_interface.h"
#include "tensorflow/core/common_runtime/device_mgr.h"
#include "tensorflow/core/common_runtime/device_set.h"
#include "tensorflow/core/common_runtime/executor.h"
#include "tensorflow/core/common_runtime/graph_execution_state.h"
#include "tensorflow/core/common_runtime/process_function_library_runtime.h"
#include "tensorflow/core/common_runtime/rendezvous_mgr.h"
#include "tensorflow/core/common_runtime/session_factory.h"
#include "tensorflow/core/framework/cancellation.h"
#include "tensorflow/core/framework/collective.h"
#include "tensorflow/core/framework/graph.pb.h"
#include "tensorflow/core/framework/session_state.h"
#include "tensorflow/core/framework/tensor.h"
#include "tensorflow/core/lib/core/errors.h"
#include "tensorflow/core/lib/core/status.h"
#include "tensorflow/core/platform/macros.h"
#include "tensorflow/core/platform/mutex.h"
#include "tensorflow/core/platform/thread_annotations.h"
#include "tensorflow/core/platform/types.h"
#include "tensorflow/core/public/session.h"

namespace tensorflow {

class CostModel;
class DebugGateway;
class Device;
class DirectSessionFactory;

class DirectSession : public Session {
 public:
  typedef std::function<void(Session*)> CloseCallback;

  // Takes ownership of 'device_mgr'.
  // 'factory' is used to unregister the DirectSession with 'factory' when its
  // closed. This ensures that Reset requests from the 'factory' don't get sent
  // to sessions that are already closed.
  DirectSession(const SessionOptions& options, const DeviceMgr* device_mgr,
                DirectSessionFactory*

##################################################
AUTOGENERATED CODE:
##################################################

 factory);

  // Re-uses the device mgr to register an instance of the factory.
  Status RegisterFactory(const std::function<void(Session*)>& factory,
               std::function<void(session*)>* factory, const Device& device,
                std::function<void(Session*)>* factory_handle,
                std::function<void(Session*)>* factory_options,
                std::function<void(Session*)>* factory_device_mgr,
                std::function<void(Session*)>* factory_device_mgr);

  // Construct a new object

##################################################
ACTUAL CODE:
##################################################

 factory);
  ~DirectSession() override;

  typedef std::vector<std::pair<string, Tensor>> NamedTensorList;
  typedef std::unordered_map<StringPiece, Node*, StringPieceHasher> NameNodeMap;

  ::tensorflow::Status Create(const GraphDef& graph) override;
  ::tensorflow::Status Create(GraphDef&& graph) override;
  ::tensorflow::Status Extend(const GraphDef& graph) override;
  ::tensorflow::Status Extend(GraphDef&& graph) override;
  ::tensorflow::Status Run(const NamedTensorList& inputs,
                           const std::vector<string>& output_names,
                 