require 'rubygems'
require 'openssl'
require 'sinatra'
require 'json'


SHARED_SECRET = 'c27e823b0a500a537990dcccfc50334fe814fbd2'

# Handle echo requests
get '/account/endpoint' do
    content_type :json
    echo_value = params['echo']
    puts 'echo value:'
    puts(echo_value)

    status 200
    { :echo => echo_value }.to_json
end

# Handle the incoming webhook events
post '/account/endpoint' do
  request.body.rewind
  data = request.body.read
  HMAC_DIGEST = OpenSSL::Digest.new('sha1')
  signature = OpenSSL::HMAC.hexdigest(HMAC_DIGEST, SHARED_SECRET, data)
  incoming_signature = env['HTTP_PYWEBHOOKS_SIGNATURE']

  puts 'hmac verification results:'
  puts Rack::Utils.secure_compare(signature, incoming_signature)

  incoming_event = env['HTTP_EVENT']
  puts 'incoming event is:'
  puts incoming_event
  puts 'incoming json is:'
  puts data

  status 200
  '{}'
end
